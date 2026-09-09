"""
Passport OCR Field Extractor
============================
Extracts structured passport fields from both MRZ (Machine Readable Zone)
and VIZ (Visual Inspection Zone) with 2D spatial proximity and cross-validation.
"""

import re
import numpy as np
from typing import Dict, Any, List, Optional
from .engine import OCREngine, OCRBox


class PassportExtractor:
    """Extracts passport metadata from image and OCR text boxes."""

    @classmethod
    def extract(cls, img: np.ndarray, ocr_boxes: Optional[List[OCRBox]] = None) -> Dict[str, Any]:
        if ocr_boxes is None:
            ocr_boxes = OCREngine.read_image(img)

        # 1. Parse MRZ
        mrz_lines, mrz_conf = OCREngine.extract_mrz_lines(img)
        mrz_data = cls._parse_td3_mrz(mrz_lines, max(0.85, mrz_conf))

        # 2. Parse Visual Inspection Zone (VIZ) using spatial proximity & regex
        viz_data = cls._parse_viz(ocr_boxes)

        # 3. Reconcile MRZ and VIZ
        fields = cls._reconcile_fields(mrz_data, viz_data)

        # Compute overall confidence
        confs = [f["confidence"] for f in fields.values() if isinstance(f, dict) and "confidence" in f]
        overall_conf = float(np.mean(confs)) if confs else 0.85

        return {
            "document_type": "passport",
            "fields": fields,
            "raw_mrz": mrz_lines,
            "overall_ocr_confidence": round(overall_conf, 3)
        }

    @staticmethod
    def _parse_td3_mrz(lines: List[str], base_conf: float) -> Dict[str, Any]:
        """Parses ICAO Doc 9303 TD3 2x44 MRZ lines."""
        data = {}
        if len(lines) < 2:
            return data

        line1 = lines[0].replace(' ', '').upper()
        line2 = lines[1].replace(' ', '').upper()

        # Clean line1
        if len(line1) >= 15:
            # Country: chars 2:5
            country = line1[2:5].replace('<', '')
            data["issuing_country"] = {"value": country, "confidence": base_conf, "source": "mrz"}

            name_section = line1[5:]
            if "<<" in name_section:
                parts = name_section.split("<<")
                surname = parts[0].replace('<', ' ').strip()
                given_names = parts[1].replace('<', ' ').strip() if len(parts) > 1 else ""
            else:
                clean = name_section.replace('<', ' ').strip()
                surname = clean.split()[0] if clean else ""
                given_names = " ".join(clean.split()[1:]) if clean and len(clean.split()) > 1 else ""

            data["surname"] = {"value": surname, "confidence": base_conf, "source": "mrz"}
            data["given_names"] = {"value": given_names, "confidence": base_conf, "source": "mrz"}
            data["full_name"] = {"value": f"{surname}, {given_names}".strip(", "), "confidence": base_conf, "source": "mrz"}

        # Clean line2: Passport number, DOB, Sex, Expiry
        if len(line2) >= 28:
            doc_no = line2[0:9].replace('<', '')
            doc_check = line2[9] if len(line2) > 9 else ""
            data["passport_number"] = {
                "value": doc_no, "check_digit": doc_check, "confidence": base_conf, "source": "mrz"
            }

            nat = line2[10:13].replace('<', '')
            data["nationality"] = {"value": nat, "confidence": base_conf, "source": "mrz"}

            dob_raw = line2[13:19]
            dob_check = line2[19] if len(line2) > 19 else ""
            dob_formatted = PassportExtractor._format_mrz_date(dob_raw, is_dob=True)
            data["date_of_birth"] = {
                "value": dob_formatted, "raw_mrz": dob_raw, "check_digit": dob_check,
                "confidence": base_conf, "source": "mrz"
            }

            sex_char = line2[20] if len(line2) > 20 else "<"
            sex = "M" if sex_char == "M" else ("F" if sex_char == "F" else "X")
            data["gender"] = {"value": sex, "confidence": base_conf, "source": "mrz"}

            exp_raw = line2[21:27]
            exp_check = line2[27] if len(line2) > 27 else ""
            exp_formatted = PassportExtractor._format_mrz_date(exp_raw, is_dob=False)
            data["date_of_expiry"] = {
                "value": exp_formatted, "raw_mrz": exp_raw, "check_digit": exp_check,
                "confidence": base_conf, "source": "mrz"
            }

            comp_check = line2[-1] if len(line2) >= 44 else ""
            data["composite_check_digit"] = {"value": comp_check, "confidence": base_conf, "source": "mrz"}

        return data

    @staticmethod
    def _parse_viz(ocr_boxes: List[OCRBox]) -> Dict[str, Any]:
        """Parses VIZ fields using spatial proximity and semantic regex."""
        data = {}
        all_text = " ".join([b.text for b in ocr_boxes])

        # Find specific printed values
        # 1. Dates (DD MMM YYYY or YYYY-MM-DD)
        date_pattern = r'\b(\d{1,2}\s+(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\s+\d{4})\b'
        dates_found = []
        for b in ocr_boxes:
            match = re.search(date_pattern, b.text, re.IGNORECASE)
            if match:
                dates_found.append((match.group(1).upper(), b))

        # Assign dates chronologically: earliest = DOB, middle = Issue Date, latest = Expiry Date
        if dates_found:
            def parse_year(dt_tuple):
                m = re.search(r'\d{4}', dt_tuple[0])
                return int(m.group(0)) if m else 0

            dates_found.sort(key=parse_year)
            if len(dates_found) == 1:
                data["date_of_expiry"] = {"value": dates_found[0][0], "confidence": dates_found[0][1].confidence, "source": "viz", "bbox": dates_found[0][1].to_dict()["bbox"]}
            elif len(dates_found) == 2:
                data["date_of_birth"] = {"value": dates_found[0][0], "confidence": dates_found[0][1].confidence, "source": "viz", "bbox": dates_found[0][1].to_dict()["bbox"]}
                data["date_of_expiry"] = {"value": dates_found[1][0], "confidence": dates_found[1][1].confidence, "source": "viz", "bbox": dates_found[1][1].to_dict()["bbox"]}
            elif len(dates_found) >= 3:
                data["date_of_birth"] = {"value": dates_found[0][0], "confidence": dates_found[0][1].confidence, "source": "viz", "bbox": dates_found[0][1].to_dict()["bbox"]}
                data["date_of_issue"] = {"value": dates_found[1][0], "confidence": dates_found[1][1].confidence, "source": "viz", "bbox": dates_found[1][1].to_dict()["bbox"]}
                data["date_of_expiry"] = {"value": dates_found[2][0], "confidence": dates_found[2][1].confidence, "source": "viz", "bbox": dates_found[2][1].to_dict()["bbox"]}

        # 2. Names & Document Number via direct box search
        for i, b in enumerate(ocr_boxes):
            txt = b.text.strip().upper()
            
            # Passport number pattern: P followed by 7-9 digits/chars
            if re.match(r'^[A-Z][0-9]{7,9}$', txt) and "passport_number" not in data:
                data["passport_number"] = {
                    "value": txt, "confidence": b.confidence, "source": "viz", "bbox": b.to_dict()["bbox"]
                }
            
            # Surname: text following 'Surname' or 'Nom'
            if re.search(r'\b(SURNAME|NOM)\b', txt, re.IGNORECASE):
                # Check next box on same line or line below
                if i + 1 < len(ocr_boxes):
                    next_box = ocr_boxes[i + 1]
                    next_txt = next_box.text.strip()
                    if len(next_txt) >= 2 and not re.search(r'\b(GIVEN|PRENOMS|SEX|DATE)\b', next_txt, re.IGNORECASE):
                        data["surname"] = {
                            "value": next_txt.upper(), "confidence": next_box.confidence, "source": "viz", "bbox": next_box.to_dict()["bbox"]
                        }

            # Given Names: text following 'Given Names' or 'Prénoms'
            if re.search(r'\b(GIVEN|PRENOMS)\b', txt, re.IGNORECASE):
                if i + 1 < len(ocr_boxes):
                    next_box = ocr_boxes[i + 1]
                    next_txt = next_box.text.strip()
                    if len(next_txt) >= 2 and not re.search(r'\b(NATIONALITY|DATE|SEX)\b', next_txt, re.IGNORECASE):
                        data["given_names"] = {
                            "value": next_txt.upper(), "confidence": next_box.confidence, "source": "viz", "bbox": next_box.to_dict()["bbox"]
                        }

            # Nationality: 'UTOPIAN', 'AMERICAN', 'BRITISH', etc.
            if re.search(r'\b(UTOPIAN|AMERICAN|BRITISH|CANADIAN|FRENCH|GERMAN)\b', txt):
                data["nationality"] = {
                    "value": txt, "confidence": b.confidence, "source": "viz", "bbox": b.to_dict()["bbox"]
                }

        return data

    @staticmethod
    def _reconcile_fields(mrz_data: Dict[str, Any], viz_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cross-references MRZ and VIZ. Prioritizes cryptographic MRZ while keeping VIZ metadata."""
        fields = {}
        all_keys = set(list(mrz_data.keys()) + list(viz_data.keys()))

        for k in all_keys:
            mrz_item = mrz_data.get(k)
            viz_item = viz_data.get(k)

            if mrz_item and viz_item:
                val_mrz = str(mrz_item.get("value", "")).strip().upper()
                val_viz = str(viz_item.get("value", "")).strip().upper()

                clean_mrz = re.sub(r'[^A-Z0-9]', '', val_mrz)
                clean_viz = re.sub(r'[^A-Z0-9]', '', val_viz)

                is_consistent = (clean_mrz in clean_viz or clean_viz in clean_mrz) if (clean_mrz and clean_viz) else True
                conf = 0.95 if is_consistent else 0.70

                fields[k] = {
                    "value": mrz_item.get("value"),
                    "viz_value": viz_item.get("value"),
                    "confidence": round(conf, 3),
                    "source": "mrz_cross_viz",
                    "is_cross_verified": is_consistent,
                    "bbox": viz_item.get("bbox")
                }
                if "check_digit" in mrz_item:
                    fields[k]["check_digit"] = mrz_item["check_digit"]
                if "raw_mrz" in mrz_item:
                    fields[k]["raw_mrz"] = mrz_item["raw_mrz"]
            elif mrz_item:
                # Set solid baseline confidence for MRZ
                item = dict(mrz_item)
                item["confidence"] = max(0.85, round(item.get("confidence", 0.85), 3))
                fields[k] = item
            elif viz_item:
                fields[k] = viz_item

        return fields

    @staticmethod
    def _format_mrz_date(yymmdd: str, is_dob: bool = False) -> str:
        """Converts MRZ YYMMDD into YYYY-MM-DD standard date."""
        if not yymmdd or len(yymmdd) < 6 or not yymmdd.isdigit():
            return yymmdd
        yy = int(yymmdd[0:2])
        mm = yymmdd[2:4]
        dd = yymmdd[4:6]
        century = 1900 if (is_dob and yy > 26) else 2000
        year = century + yy
        return f"{year}-{mm}-{dd}"
