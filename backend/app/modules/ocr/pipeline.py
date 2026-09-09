"""
Module 1 — OCR Extraction and Classification Pipeline
======================================================
Unified entry point for document loading, orientation deskewing,
document type classification, field extraction, and confidence scoring.
"""

import time
import numpy as np
from typing import Dict, Any, Optional
from .preprocessor import DocumentPreprocessor
from .engine import OCREngine, OCRBox
from .classifier import DocumentClassifier
from .passport_extractor import PassportExtractor
from .visa_extractor import VisaExtractor
from .id_extractor import IdCardExtractor


class OCRPipeline:
    """Master pipeline coordinating OCR and document field extraction."""

    @classmethod
    def process_document(
        cls,
        document_input,
        user_document_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processes document input (file path, raw bytes, or numpy array).
        Returns comprehensive structured JSON:
        {
            "success": True,
            "processing_time_ms": float,
            "document_info": {"width": int, "height": int, "channels": int},
            "classification": {"document_type": str, "confidence": float, "reason": str},
            "fields": {
                "<field_name>": {"value": str, "confidence": float, "source": str, "bbox": dict}
            },
            "raw_mrz": [str],
            "ocr_boxes": [dict],
            "overall_ocr_confidence": float
        }
        """
        start_time = time.time()

        # 1. Load and deskew
        raw_img = DocumentPreprocessor.load_image(document_input)
        aligned_img = DocumentPreprocessor.deskew(raw_img)
        h, w = aligned_img.shape[:2]

        # 2. Extract OCR words/boxes
        ocr_boxes = OCREngine.read_image(aligned_img)

        # 3. Classify document type
        classification = DocumentClassifier.classify(
            img=aligned_img,
            ocr_boxes=ocr_boxes,
            user_hint=user_document_type
        )
        doc_type = classification["document_type"]

        # 4. Route to specialized extractor
        if doc_type == "passport":
            extracted = PassportExtractor.extract(aligned_img, ocr_boxes)
        elif doc_type == "visa":
            extracted = VisaExtractor.extract(aligned_img, ocr_boxes)
        else:
            # National ID / Driving License / Permit
            extracted = IdCardExtractor.extract(aligned_img, ocr_boxes)

        elapsed_ms = round((time.time() - start_time) * 1000, 1)

        return {
            "success": True,
            "processing_time_ms": elapsed_ms,
            "document_info": {
                "width": int(w),
                "height": int(h),
                "channels": int(aligned_img.shape[2]) if len(aligned_img.shape) == 3 else 1
            },
            "classification": classification,
            "fields": extracted.get("fields", {}),
            "raw_mrz": extracted.get("raw_mrz", []),
            "overall_ocr_confidence": extracted.get("overall_ocr_confidence", 0.8),
            "ocr_boxes": [b.to_dict() for b in ocr_boxes]
        }
