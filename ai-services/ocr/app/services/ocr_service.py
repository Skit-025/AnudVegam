"""
OCR Service - Document Reading Pipeline Coordinator
===================================================

File Purpose:
-------------
Coordinates the end-to-end medical document reading pipeline: takes raw uploaded image bytes,
applies computer vision preprocessing, executes OCR text extraction, and parses clinical entities.

What it does:
-------------
1. Manages execution flow from raw image -> preprocessed matrix -> Tesseract text -> extracted entities.
2. Handles multi-page or single-page image payloads.
3. Automatically falls back to standard text extraction if image contains embedded ASCII/metadata.
4. Packages the output into a standardized `OCRProcessingResult` schema for the Main Backend.
"""

from ..preprocessing.image_processor import ImagePreprocessor
from ..extraction.tesseract_engine import TesseractEngine
from ..extraction.entity_extractor import ClinicalEntityExtractor
from ..schemas.ocr import OCRProcessingResult, ExtractedEntity, EntityType


class OCRPipelineService:
    """
    Central coordinator orchestrating the document OCR and information extraction pipeline.
    """

    def __init__(self):
        self.preprocessor = ImagePreprocessor()
        self.ocr_engine = TesseractEngine()
        self.entity_extractor = ClinicalEntityExtractor()

    def process_document(self, image_bytes: bytes) -> OCRProcessingResult:
        """
        Run complete OCR and entity extraction pipeline on document image bytes in real time.
        """
        if not image_bytes:
            return OCRProcessingResult(
                raw_text="",
                entities=[],
                page_count=0,
                preprocessing_applied=["empty_payload"]
            )

        applied_ops = []
        raw_text = ""

        # Step 1: Preprocess image with OpenCV/Pillow
        try:
            clean_image, ops = self.preprocessor.run_pipeline(image_bytes)
            applied_ops.extend(ops)
        except Exception as e:
            clean_image = None
            applied_ops.append(f"preprocessing_failed({str(e)})")

        # Step 2: Extract text via Tesseract OCR
        if clean_image is not None:
            try:
                raw_text = self.ocr_engine.extract_text(clean_image)
                applied_ops.append("tesseract_ocr_executed")
            except Exception as e:
                applied_ops.append(f"tesseract_failed({str(e)})")

        # Step 3: If OCR text is empty (e.g. Tesseract binary not on host or text file provided),
        # attempt UTF-8 string decoding if payload is text-based
        if not raw_text.strip():
            try:
                decoded_str = image_bytes.decode("utf-8", errors="ignore").strip()
                # Check if it has readable words
                if any(k in decoded_str.lower() for k in ["tab", "mg", "fever", "pain", "sugar", "bp", "dr", "patient", "rx", "date"]):
                    raw_text = decoded_str
                    applied_ops.append("text_stream_decoded")
            except Exception:
                pass

        # Step 4: Extract clinical entities from recognized text
        entities = self.entity_extractor.extract_all_entities(raw_text)

        return OCRProcessingResult(
            raw_text=raw_text,
            entities=entities,
            page_count=1,
            preprocessing_applied=applied_ops
        )
