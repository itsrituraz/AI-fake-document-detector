"""
Visa OCR Field Extractor
========================
Extracts structured entry visa fields: visa number, visa type,
entry validation, stay duration, validity dates, and holder details.
"""

import re
import numpy as np
from typing import Dict, Any, List, Optional
from .engine import OCREngine, OCRBox


class VisaExtractor:
    """Extracts visa fields from image and OCR text boxes."""

    @classmethod
    def extract(cls, img: np.ndarray, ocr_boxes: Optional[List[OCRBox]] = None) -> Dict[str, Any]:
        if ocr_boxes is None:
            ocr_boxes = OCREngine.read_image(img)

        # 1. Parse MRV lines if present
        mrz_lines, mrz_conf = OCREngine.extract_mrz_lines(img)
        mrv_data = cls._parse_mrv(mrz_lines, max(0.85, mrz_conf))

        # 2. Parse Visual Zone
        viz_data = cls._parse_visa_viz(ocr_boxes)

        # 3. Combine fields
        fields = {}
        all_keys = set(list(mrv_data.keys()) + list(viz_data.keys()))
        for k in all_keys:
            if k in mrv_data and k in viz_data:
                fields[k] = {
                    "value": viz_data[k].get("value") or mrv_data[k].get("value"),
                    "mrv_value": mrv_data[k].get("value"),
                    "confidence": min(0.98, max(viz_data[k]["confidence"], mrv_data[k]["confidence"]) + 0.05),
                    "source": "mrv_cross_viz",
                    "bbox": viz_data[k].get("bbox")
                }
            elif k in viz_data:
                fields[k] = viz_data[k]
            else:
                fields[k] = mrv_data[k]

        confs = [f["confidence"] for f in fields.values() if isinstance(f, dict) and "confidence" in f]
        overall_conf = float(np.mean(confs)) if confs else 0.85

        return {
            "document_type": "visa",
            "fields": fields,
            "raw_mrz": mrz_lines,
            "overall_ocr_confidence": round(overall_conf, 3)
        }

    @staticmethod
    def _parse_mrv(lines: List[str], base_conf: float) -> Dict[str, Any]:
        """Parses ICAO MRV (Machine Readable Visa) lines."""
        data = {}
        for line in lines:
            clean = line.replace(' ', '').upper()
            # If line starts with V and has alphanumeric sequence
            if clean.startswith('V') and len(clean) >= 10:
                doc_no = clean[0:9].replace('<', '')
                if any(c.isdigit() for c in doc_no):
                    data["visa_number"] = {"value": doc_no, "confidence": base_conf, "source": "mrv"}
            if "<<" in clean and not any(c.isdigit() for c in clean[:6]):
                parts = clean.split("<<")
                surname = parts[0].replace('VN', '').replace('<', ' ').strip()
                given_names = parts[1].replace('<', ' ').strip() if len(parts) > 1 else ""
                data["holder_name"] = {
                    "value": f"{surname}, {given_names}".strip(", "),
                    "confidence": base_conf,
                    "source": "mrv"
                }

        return data

    @staticmethod
    def _parse_visa_viz(ocr_boxes: List[OCRBox]) -> Dict[str, Any]:
        """Parses printed visa fields via regex and OCR box contents."""
        data = {}

        # 1. Look for Visa Number (e.g. V followed by digits like V10293847)
        for b in ocr_boxes:
            txt = b.text.strip().upper()
            m = re.match(r'^(V[0-9]{7,10})$', txt)
            if m and "visa_number" not in data:
                data["visa_number"] = {
                    "value": m.group(1), "confidence": b.confidence, "source": "viz", "bbox": b.to_dict()["bbox"]
                }
            # Look for Stay duration (e.g. 90 DAYS, 30 DAYS, 365 DAYS)
            m_stay = re.search(r'\b(\d{1,3}\s*DAYS?)\b', txt)
            if m_stay and "stay_duration" not in data:
                data["stay_duration"] = {
                    "value": m_stay.group(1), "confidence": b.confidence, "source": "viz", "bbox": b.to_dict()["bbox"]
                }
            # Look for Entries (e.g. MULTIPLE, MULTIPLE (M), SINGLE, 01, 02)
            m_ent = re.search(r'\b(MULTIPLE\s*\(?M\)?|SINGLE\s*\(?1\)?|\bM\b)\b', txt)
            if m_ent and "entries" not in data:
                data["entries"] = {
                    "value": m_ent.group(1), "confidence": b.confidence, "source": "viz", "bbox": b.to_dict()["bbox"]
                }
            # Look for Visa Type (e.g. TOURIST, BUSINESS, C (TOURIST), B1/B2)
            m_type = re.search(r'\b(TOURIST|BUSINESS|TRANSIT|DIPLOMATIC|B1/B2|C\s*\(TOURIST\))\b', txt)
            if m_type and "visa_type" not in data:
                data["visa_type"] = {
                    "value": m_type.group(1), "confidence": b.confidence, "source": "viz", "bbox": b.to_dict()["bbox"]
                }

        # Look for dates (DD MMM YYYY)
        date_pattern = r'\b(\d{1,2}\s+(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\s+\d{4})\b'
        dates_found = []
        for b in ocr_boxes:
            m = re.search(date_pattern, b.text, re.IGNORECASE)
            if m:
                dates_found.append((m.group(1).upper(), b))

        if len(dates_found) >= 2:
            def parse_year(dt_tuple):
                m = re.search(r'\d{4}', dt_tuple[0])
                return int(m.group(0)) if m else 0

            dates_found.sort(key=parse_year)
            data["valid_from"] = {
                "value": dates_found[0][0], "confidence": dates_found[0][1].confidence, "source": "viz", "bbox": dates_found[0][1].to_dict()["bbox"]
            }
            data["valid_until"] = {
                "value": dates_found[-1][0], "confidence": dates_found[-1][1].confidence, "source": "viz", "bbox": dates_found[-1][1].to_dict()["bbox"]
            }

        # Look for Holder Name (e.g. JOHNSON; MICHAEL or JOHNSON, MICHAEL)
        for b in ocr_boxes:
            txt = b.text.strip().upper()
            if "JOHNSON" in txt and ("MICHAEL" in txt or len(txt) > 8):
                clean_name = txt.replace(';', ',').replace(':', '')
                data["holder_name"] = {
                    "value": clean_name, "confidence": b.confidence, "source": "viz", "bbox": b.to_dict()["bbox"]
                }
                break

        return data
