"""
Main Backend - Security & Authentication Utilities
==================================================

File Purpose:
-------------
Provides session token generation, cryptographic signing, password hashing,
and mock ABHA / Aadhaar identity token verification.

What it does:
-------------
1. Generates signed JWT session tokens using HMAC-SHA256.
2. Validates and decodes kiosk session tokens.
3. Implements ABDM / ABHA 14-digit validation and demographic retrieval.
"""

import hmac
import hashlib
import json
import base64
import time
import re
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from .config import settings


class SecurityManager:
    """
    Handles token creation, verification, and mock ABDM/ABHA identity checking.
    """

    def __init__(self):
        self.secret_key = settings.SECRET_KEY.encode("utf-8")
        self.algorithm = settings.ALGORITHM

    def _base64url_encode(self, data: bytes) -> str:
        return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

    def _base64url_decode(self, data: str) -> bytes:
        rem = len(data) % 4
        if rem > 0:
            data += "=" * (4 - rem)
        return base64.urlsafe_b64decode(data.encode("utf-8"))

    def create_session_token(self, session_id: str, expires_delta: Optional[timedelta] = None) -> str:
        """
        Generate a cryptographically signed session token for a kiosk session.
        """
        expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        if expires_delta:
            exp = int((datetime.utcnow() + expires_delta).timestamp())
        else:
            exp = int((datetime.utcnow() + timedelta(minutes=expire_minutes)).timestamp())

        header = {"alg": "HS256", "typ": "JWT"}
        payload = {"sub": session_id, "iat": int(time.time()), "exp": exp}

        hdr_b64 = self._base64url_encode(json.dumps(header).encode("utf-8"))
        pld_b64 = self._base64url_encode(json.dumps(payload).encode("utf-8"))
        msg = f"{hdr_b64}.{pld_b64}".encode("utf-8")
        sig = hmac.new(self.secret_key, msg, hashlib.sha256).digest()
        sig_b64 = self._base64url_encode(sig)

        return f"{hdr_b64}.{pld_b64}.{sig_b64}"

    def verify_session_token(self, token: str) -> Optional[str]:
        """
        Decode and validate kiosk session token signature and expiration.
        """
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None

            hdr_b64, pld_b64, sig_b64 = parts
            msg = f"{hdr_b64}.{pld_b64}".encode("utf-8")
            expected_sig = hmac.new(self.secret_key, msg, hashlib.sha256).digest()
            actual_sig = self._base64url_decode(sig_b64)

            if not hmac.compare_digest(expected_sig, actual_sig):
                return None

            payload = json.loads(self._base64url_decode(pld_b64).decode("utf-8"))
            if payload.get("exp", 0) < time.time():
                return None

            return payload.get("sub")
        except Exception:
            return None

    def verify_mock_abha(self, abha_id: str) -> Dict[str, Any]:
        """
        Simulate ABHA (Ayushman Bharat Health Account) 14-digit identifier validation.
        """
        clean_id = re.sub(r"[\s\-]", "", abha_id)
        is_valid_format = len(clean_id) == 14 and clean_id.isdigit()

        # Format as standard XX-XXXX-XXXX-XXXX
        formatted_abha = f"{clean_id[:2]}-{clean_id[2:6]}-{clean_id[6:10]}-{clean_id[10:]}" if len(clean_id) == 14 else abha_id

        # Return realistic KYC record
        return {
            "verified": is_valid_format,
            "abha_id": formatted_abha,
            "name": "Ramesh Kumar" if clean_id.endswith("12") else "Sunita Devi",
            "gender": "MALE" if clean_id.endswith("12") else "FEMALE",
            "age": 45 if clean_id.endswith("12") else 58,
            "phone": "9876543210",
            "mock_kyc_status": "SUCCESS" if is_valid_format else "INVALID_FORMAT"
        }
