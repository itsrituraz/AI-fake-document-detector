"""
National ID & Driver License OCR Field Extractor
================================================
Extracts identification cards, driver licenses, and residency permits.
"""

import re
import numpy as np
from typing import Dict, Any, List, Optional
from .engine import OCREngine, OCRBox


class IdCardExtractor:
    """Extracts metadata from national ID cards, driver licenses, and permits."""

    @classmethod
    def extract(cls, img: np.ndarray, ocr_boxes: Optional[List[OCRBox]] = None) -> Dict[str, Any]:
        """Extracts identification fields with confidence scoring."""
        if ocr_boxes is None:
            ocr_boxes = OCREngine.read_image(img)

        full_text = " \n ".join([b.text for b in ocr_boxes])
        fields = {}

        patterns = {
            "document_number": r'(?:Licence\s*No|License\s*No|ID\s*No|Document\s*No|Card\s*No)[.:\s/]*([A-Z0-9\-\s]{6,14})',
            "full_name": r'(?:Name|Nom|Full\s*Name|Holder)[.:\s/]*([A-Z\s\-]+?)(?=\n|DOB|\bDate\b|$)',
            "date_of_birth": r'(?:DOB|Date\s*of\s*Birth|Born)[.:\s/]*(\d{1,2}\s+[A-Z]{3,4}\s+\d{4}|\d{2}[-./]\d{2}[-./]\d{4})',
            "date_of_expiry": r'(?:Expiry|Expires|Valid\s*Until)[.:\s/]*(\d{1,2}\s+[A-Z]{3,4}\s+\d{4}|\d{2}[-./]\d{2}[-./]\d{4})',
            "date_of_issue": r'(?:Issued|Issue\s*Date)[.:\s/]*(\d{1,2}\s+[A-Z]{3,4}\s+\d{4}|\d{2}[-./]\d{2}[-./]\d{4})',
            "category": r'(?:Class|Category|Permit\s*Type)[.:\s/]*([A-Z0-9\s]+?)(?=\n|$)'
        }

        for field, pat in patterns.items():
            match = re.search(pat, full_text, re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                matching_box = None
                for b in ocr_boxes:
                    if val.upper() in b.text.upper() or (len(val) > 3 and val.upper()[:3] in b.text.upper()):
                        matching_box = b.to_dict()["bbox"]
                        break

                fields[field] = {
                    "value": val,
                    "confidence": 0.84,
                    "source": "viz",
                    "bbox": matching_box
                }

        # Check TD1 3-line MRZ if present on back of ID card
        mrz_lines, mrz_conf = OCREngine.extract_mrz_lines(img)
        if len(mrz_lines) == 3:
            # TD1 Format: 3 lines x 30 chars
            line1, line2, line3 = mrz_lines[0], mrz_lines[1], mrz_lines[2]
            if len(line1) >= 15:
                doc_num = line1[5:14].replace('<', '')
                fields["document_number"] = {
                    "value": doc_num, "confidence": mrz_conf, "source": "mrz"
                }

        confs = [f["confidence"] for f in fields.values() if isinstance(f, dict) and "confidence" in f]
        overall_conf = float(np.mean(confs)) if confs else 0.5

        return {
            "document_type": "national_id",
            "fields": fields,
            "raw_mrz": mrz_lines,
            "overall_ocr_confidence": round(overall_conf, 3)
        }
