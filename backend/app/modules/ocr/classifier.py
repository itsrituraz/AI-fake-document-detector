"""
Document Type Classification Engine
===================================
Classifies identity documents into Passport, Visa, National ID,
or Driving License using MRZ indicators and visual header keywords.
"""

import re
import numpy as np
from typing import Optional, Dict, Any, List
from .engine import OCREngine, OCRBox


class DocumentClassifier:
    """Classifies document types from optical content and user hints."""

    SUPPORTED_TYPES = ["passport", "visa", "national_id", "driving_license", "residence_permit"]

    @classmethod
    def classify(
        cls,
        img: np.ndarray,
        ocr_boxes: Optional[List[OCRBox]] = None,
        user_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Determines document type.
        If user_hint is provided and not 'auto', honors user override with validation.
        Returns:
            {
                "document_type": "passport" | "visa" | "national_id" | "driving_license",
                "confidence": 0.0 - 1.0,
                "reason": str,
                "is_mrz_present": bool,
                "detected_type": str
            }
        """
        if ocr_boxes is None:
            ocr_boxes = OCREngine.read_image(img)

        # 1. Inspect MRZ zone indicators
        mrz_lines, mrz_conf = OCREngine.extract_mrz_lines(img)
        is_mrz_present = len(mrz_lines) >= 2

        detected_type = "unknown"
        confidence = 0.5
        reasons = []

        # Check MRZ starting character tags
        if is_mrz_present:
            first_line = mrz_lines[0].upper()
            if first_line.startswith("P<") or first_line.startswith("P"):
                detected_type = "passport"
                confidence = max(0.92, mrz_conf)
                reasons.append("Detected ICAO TD3 Passport MRZ format (starts with 'P<')")
            elif first_line.startswith("V<") or first_line.startswith("VN"):
                detected_type = "visa"
                confidence = max(0.90, mrz_conf)
                reasons.append("Detected ICAO MRV Machine Readable Visa format (starts with 'V<')")
            elif first_line.startswith("I<") or first_line.startswith("ID") or len(mrz_lines) == 3:
                detected_type = "national_id"
                confidence = max(0.88, mrz_conf)
                reasons.append("Detected ICAO TD1 3-line National Identity MRZ format")

        # 2. Check visual header keywords (upper 35% of image)
        h = img.shape[0]
        header_text = " ".join([
            b.text.upper() for b in ocr_boxes if b.y < h * 0.35
        ])
        all_text = " ".join([b.text.upper() for b in ocr_boxes])

        if detected_type == "unknown":
            if re.search(r'\b(PASSPORT|PASSEPORT|REISEPASS|PASAPORTE)\b', header_text):
                detected_type = "passport"
                confidence = 0.88
                reasons.append("Header matches official Passport title")
            elif re.search(r'\b(VISA|SCHENGEN|ENTRY VISA|IMMIGRATION VISA)\b', header_text):
                detected_type = "visa"
                confidence = 0.88
                reasons.append("Header matches official Entry Visa title")
            elif re.search(r'\b(DRIVING LICENCE|DRIVER LICENSE|DRIVER\'S LICENSE|PERMIS DE CONDUIRE)\b', all_text):
                detected_type = "driving_license"
                confidence = 0.86
                reasons.append("Text matches Driving License keywords")
            elif re.search(r'\b(IDENTITY CARD|NATIONAL ID|CITIZEN CARD|CEDULA)\b', all_text):
                detected_type = "national_id"
                confidence = 0.84
                reasons.append("Text matches National Identity Card keywords")
            elif re.search(r'\b(RESIDENCE PERMIT|PERMIT TO RESIDE)\b', all_text):
                detected_type = "residence_permit"
                confidence = 0.82
                reasons.append("Text matches Residence Permit keywords")
            else:
                detected_type = "passport"  # default standard fallback
                confidence = 0.50
                reasons.append("No explicit header matched; defaulting to standard travel document inspection")

        # Handle user override if supplied
        final_type = detected_type
        if user_hint and user_hint.lower() in cls.SUPPORTED_TYPES:
            hint = user_hint.lower()
            if hint != detected_type:
                reasons.append(f"User overridden to '{hint}' (detected was '{detected_type}')")
            final_type = hint

        return {
            "document_type": final_type,
            "detected_type": detected_type,
            "confidence": round(float(confidence), 3),
            "reason": "; ".join(reasons) if reasons else "Pattern matched",
            "is_mrz_present": is_mrz_present,
            "mrz_line_count": len(mrz_lines)
        }
