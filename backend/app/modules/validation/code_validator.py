"""
Country Codes, Formats & Cross-Zone Consistency Validator
=========================================================
Validates ISO 3166-1 alpha-3 country codes, document number syntax,
and consistency between Visual Inspection Zone (VIZ) and MRZ fields.
"""

import re
from typing import Dict, Any, List, Optional

# Standard ISO 3166-1 alpha-3 + ICAO specimen/special territory codes
VALID_COUNTRY_CODES = {
    "AFG", "ALB", "DZA", "AND", "AGO", "ATG", "ARG", "ARM", "AUS", "AUT", "AZE",
    "BHS", "BHR", "BGD", "BRB", "BLR", "BEL", "BLZ", "BEN", "BTN", "BOL", "BIH",
    "BWA", "BRA", "BRN", "BGR", "BFA", "BDI", "CPV", "KHM", "CMR", "CAN", "CAF",
    "TCD", "CHL", "CHN", "COL", "COM", "COG", "CRI", "HRV", "CUB", "CYP", "CZE",
    "DNK", "DJI", "DMA", "DOM", "ECU", "EGY", "SLV", "GNQ", "ERI", "EST", "SWZ",
    "ETH", "FJI", "FIN", "FRA", "GAB", "GMB", "GEO", "DEU", "GHA", "GRC", "GRD",
    "GTM", "GIN", "GNB", "GUY", "HTI", "HND", "HUN", "ISL", "IND", "IDN", "IRN",
    "IRQ", "IRL", "ISR", "ITA", "JAM", "JPN", "JOR", "KAZ", "KEN", "KIR", "PRK",
    "KOR", "KWT", "KGZ", "LAO", "LVA", "LBN", "LSO", "LBR", "LBY", "LIE", "LTU",
    "LUX", "MDG", "MWI", "MYS", "MDV", "MLI", "MLT", "MHL", "MRT", "MUS", "MEX",
    "FSM", "MDA", "MCO", "MNG", "MNE", "MAR", "MOZ", "MMR", "NAM", "NRU", "NPL",
    "NLD", "NZL", "NIC", "NER", "NGA", "MKD", "NOR", "OMN", "PAK", "PLW", "PAN",
    "PNG", "PRY", "PER", "PHL", "POL", "PRT", "QAT", "ROU", "RUS", "RWA", "KNA",
    "LCA", "VCT", "WSM", "SMR", "STP", "SAU", "SEN", "SRB", "SYC", "SLE", "SGP",
    "SVK", "SVN", "SLB", "SOM", "ZAF", "SSD", "ESP", "LKA", "SDN", "SUR", "SWE",
    "CHE", "SYR", "TWN", "TJK", "TZA", "THA", "TLS", "TGO", "TON", "TTO", "TUN",
    "TUR", "TKM", "TUV", "UGA", "UKR", "ARE", "GBR", "USA", "URY", "UZB", "VUT",
    "VAT", "VEN", "VNM", "YEM", "ZMB", "ZWE",
    # ICAO Special & Specimen codes:
    "UTO", "UTOPIA", "XPO", "XXA", "XXB", "XXX", "UNO", "UNA", "UNK"
}


class CodeAndFormatValidator:
    """Validates international country codes, syntax rules, and cross-zone consistency."""

    @classmethod
    def validate_country_code(cls, country_code: Optional[str]) -> Dict[str, Any]:
        """Validates 3-letter issuing country or nationality code."""
        if not country_code:
            return {"is_valid": False, "code": "", "flag": "Missing country or nationality code"}

        clean = country_code.strip().upper().replace('<', '')
        # Direct match or substring
        is_valid = clean in VALID_COUNTRY_CODES
        flag = None if is_valid else f"Unrecognized ISO 3166-1 alpha-3 country/nationality code: '{clean}'"

        return {
            "is_valid": is_valid,
            "code": clean,
            "flag": flag
        }

    @classmethod
    def validate_document_number_format(cls, doc_type: str, doc_number: Optional[str]) -> Dict[str, Any]:
        """Validates alphanumeric format and length rules per document type."""
        if not doc_number:
            return {"is_valid": False, "flag": "Missing document number"}

        clean = doc_number.strip().upper().replace(' ', '')
        flags = []

        if len(clean) < 6 or len(clean) > 15:
            flags.append(f"Abnormal document number length ({len(clean)} characters; standard is 7-10)")

        if not re.match(r'^[A-Z0-9]+$', clean):
            flags.append(f"Document number contains invalid characters: '{clean}' (must be strictly alphanumeric)")

        if doc_type == "passport":
            # Passports typically begin with 1 or 2 letters followed by digits
            if not re.match(r'^[A-Z0-9]{8,10}$', clean):
                flags.append(f"Unusual passport number format: '{clean}'")

        return {
            "is_valid": len(flags) == 0,
            "document_number": clean,
            "flags": flags
        }

    @classmethod
    def validate_cross_zone_consistency(cls, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cross-checks values between the printed visual inspection zone (VIZ)
        and the Machine Readable Zone (MRZ). Mismatches strongly indicate digital tampering.
        """
        discrepancies = []

        # Check Name consistency
        surname_field = fields.get("surname", {})
        if isinstance(surname_field, dict):
            mrz_val = surname_field.get("value", "")
            viz_val = surname_field.get("viz_value", "")
            if mrz_val and viz_val:
                c_mrz = re.sub(r'[^A-Z]', '', mrz_val.upper())
                c_viz = re.sub(r'[^A-Z]', '', viz_val.upper())
                if c_mrz and c_viz and c_mrz not in c_viz and c_viz not in c_mrz:
                    discrepancies.append(f"Surname mismatch: MRZ says '{mrz_val}' but printed VIZ says '{viz_val}'")

        # Check Expiry Date consistency
        exp_field = fields.get("date_of_expiry", {})
        if isinstance(exp_field, dict):
            mrz_exp = exp_field.get("value", "")
            viz_exp = exp_field.get("viz_value", "")
            if mrz_exp and viz_exp:
                # Compare year
                m_mrz = re.search(r'\d{4}', mrz_exp)
                m_viz = re.search(r'\d{4}', viz_exp)
                if m_mrz and m_viz and m_mrz.group(0) != m_viz.group(0):
                    discrepancies.append(
                        f"CRITICAL DISCREPANCY: Expiry year in MRZ ({m_mrz.group(0)}) does NOT match printed visual zone ({m_viz.group(0)})"
                    )

        # Check Document Number consistency
        doc_field = fields.get("passport_number", {}) or fields.get("visa_number", {})
        if isinstance(doc_field, dict):
            mrz_doc = doc_field.get("value", "")
            viz_doc = doc_field.get("viz_value", "")
            if mrz_doc and viz_doc:
                c_mrz = re.sub(r'[^A-Z0-9]', '', mrz_doc.upper())
                c_viz = re.sub(r'[^A-Z0-9]', '', viz_doc.upper())
                if c_mrz and c_viz and c_mrz != c_viz:
                    discrepancies.append(f"Document number mismatch: MRZ has '{mrz_doc}' but printed body has '{viz_doc}'")

        return {
            "is_consistent": len(discrepancies) == 0,
            "discrepancies": discrepancies
        }
