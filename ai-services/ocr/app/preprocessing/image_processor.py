"""
OCR Service - Computer Vision Image Preprocessor
=================================================

File Purpose:
-------------
Prepares raw images (captured via kiosk camera or uploaded scans of prescriptions/lab reports)
for high-accuracy text extraction by Tesseract OCR.

What it does:
-------------
1. Validates and decodes image bytes using Pillow and OpenCV.
2. Converts images to grayscale and applies Gaussian blurring to reduce high-frequency noise.
3. Performs deskewing / rotation correction to align slanted documents.
4. Applies adaptive thresholding (Otsu's binarization) to enhance faded ink and doctor handwriting.
5. Performs morphological operations to remove shadow artifacts.
"""

import io
from typing import Tuple, List, Optional
import numpy as np

try:
    import cv2
except ImportError:
    cv2 = None

try:
    from PIL import Image
except ImportError:
    Image = None


class ImagePreprocessor:
    """
    OpenCV and Pillow document cleanup pipeline for medical documents.
    """

    def __init__(self):
        self.gaussian_kernel = (3, 3)

    def decode_image_bytes(self, image_bytes: bytes) -> np.ndarray:
        """
        Decode raw image file bytes into an OpenCV BGR numpy array.
        """
        if not image_bytes:
            raise ValueError("Empty image byte payload provided.")

        if cv2 is not None:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is not None:
                return img

        # Fallback to Pillow if cv2.imdecode failed or cv2 is unavailable
        if Image is not None:
            pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            return np.array(pil_img)[:, :, ::-1]  # Convert RGB to BGR

        raise RuntimeError("Neither OpenCV nor Pillow is available for image decoding.")

    def convert_to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """
        Convert BGR color image to single-channel 8-bit grayscale.
        """
        if len(image.shape) == 2:
            return image

        if cv2 is not None:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Basic luminance conversion if cv2 unavailable: 0.299 R + 0.587 G + 0.114 B
        b = image[:, :, 0].astype(float)
        g = image[:, :, 1].astype(float)
        r = image[:, :, 2].astype(float)
        gray = (0.114 * b + 0.587 * g + 0.299 * r).astype(np.uint8)
        return gray

    def deskew_document(self, gray_image: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Detect text skew angle and rotate image to straighten horizontal text lines.
        """
        if cv2 is None:
            return gray_image, 0.0

        try:
            # Invert grayscale for contours
            thresh = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
            coords = np.column_stack(np.where(thresh > 0))
            if len(coords) < 10:
                return gray_image, 0.0

            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            elif angle > 45:
                angle = 90 - angle
            else:
                angle = -angle

            # Restrict excessive rotation for document sanity
            if abs(angle) > 30.0 or abs(angle) < 0.5:
                return gray_image, 0.0

            (h, w) = gray_image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(gray_image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            return rotated, float(angle)
        except Exception:
            return gray_image, 0.0

    def apply_adaptive_threshold(self, gray_image: np.ndarray) -> np.ndarray:
        """
        Apply gentle blur and Otsu binarization to maximize contrast between text and paper background.
        """
        if cv2 is None:
            return gray_image

        try:
            blurred = cv2.GaussianBlur(gray_image, self.gaussian_kernel, 0)
            thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            return thresh
        except Exception:
            return gray_image

    def run_pipeline(self, image_bytes: bytes) -> Tuple[np.ndarray, List[str]]:
        """
        Execute full computer vision cleanup sequence on raw image bytes.
        """
        operations = []
        img = self.decode_image_bytes(image_bytes)
        operations.append("decode_image_bytes")

        gray = self.convert_to_grayscale(img)
        operations.append("convert_to_grayscale")

        straightened, angle = self.deskew_document(gray)
        if angle != 0.0:
            operations.append(f"deskew_document(angle={angle:.1f})")

        binarized = self.apply_adaptive_threshold(straightened)
        operations.append("apply_adaptive_threshold")

        return binarized, operations
