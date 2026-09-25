"""
OCR Service - Tesseract OCR Engine Wrapper
===========================================

File Purpose:
-------------
Encapsulates communication with Google Tesseract OCR engine (via `pytesseract`) to convert
preprocessed document images into machine-readable unicode text.

What it does:
-------------
1. Configures OCR engine modes (OEM) and Page Segmentation Modes (PSM) optimized for medical receipts/prescriptions.
2. Supports multilingual character recognition (English, Hindi / Devanagari script).
3. Extracts raw unicode text along with confidence metrics.
"""

from typing import Dict, Any, Optional
import numpy as np

try:
    import pytesseract
    from pytesseract import Output
except ImportError:
    pytesseract = None
    Output = None

try:
    from PIL import Image
except ImportError:
    Image = None


class TesseractEngine:
    """
    Wrapper for Tesseract OCR execution and PSM configuration.
    """

    def __init__(self, lang: str = "eng+hin", psm: int = 6):
        self.lang = lang
        self.psm = psm

    def extract_text(self, image: np.ndarray) -> str:
        """
        Run OCR on preprocessed image and return raw recognized text.
        """
        if pytesseract is None:
            return ""

        try:
            # Convert numpy array to PIL Image if needed
            if Image is not None and not isinstance(image, Image.Image):
                pil_img = Image.fromarray(image)
            else:
                pil_img = image

            config = f"--oem 3 --psm {self.psm}"
            text = pytesseract.image_to_string(pil_img, lang=self.lang, config=config)
            return text.strip()
        except Exception:
            # Try without Hindi language pack if eng+hin fails (e.g. standard English only installed)
            try:
                config = f"--oem 3 --psm {self.psm}"
                text = pytesseract.image_to_string(pil_img, lang="eng", config=config)
                return text.strip()
            except Exception:
                return ""

    def extract_data_with_confidence(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Extract detailed word-level OCR output including confidence scores.
        """
        if pytesseract is None or Output is None:
            return {"words": [], "mean_confidence": 0.0}

        try:
            if Image is not None and not isinstance(image, Image.Image):
                pil_img = Image.fromarray(image)
            else:
                pil_img = image

            config = f"--oem 3 --psm {self.psm}"
            data = pytesseract.image_to_data(pil_img, lang="eng", config=config, output_type=Output.DICT)

            valid_confs = [int(c) for c in data.get("conf", []) if str(c).isdigit() and int(c) >= 0]
            mean_conf = float(np.mean(valid_confs)) if valid_confs else 0.0

            words = [text for text in data.get("text", []) if text and text.strip()]
            return {
                "words": words,
                "mean_confidence": round(mean_conf / 100.0, 2)
            }
        except Exception:
            return {"words": [], "mean_confidence": 0.0}
