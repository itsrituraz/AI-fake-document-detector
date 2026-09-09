"""
Module 2 — Document Validation Pipeline
=======================================
Coordinates MRZ checksums, date logic, ISO codes, cross-zone verification,
and mock government watchlist/issuance queries.
"""

from typing import Dict, Any, List
from .mrz_validator import MRZValidator
from .date_validator import DateValidator
from .code_validator import CodeAndFormatValidator
from .watchlist import WatchlistService


class ValidationPipeline:
    """Master validation coordinator evaluating format, rules, and security databases."""

    @classmethod
    def validate(cls, ocr_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes complete validation checks against OCR output.
        Returns:
            {
                "is_valid": bool,
                "validation_score": float (0.0 - 1.0),
                "mrz_checks": dict,
                "date_checks": dict,
                "code_checks": dict,
                "cross_zone_checks": dict,
                "watchlist_checks": dict,
                "all_flags": List[str],
                "critical_violations": List[str]
            }
        """
        doc_type = ocr_result.get("classification", {}).get("document_type", "passport")
        fields = ocr_result.get("fields", {})
        raw_mrz = ocr_result.get("raw_mrz", [])

        all_flags = []
        critical_violations = []

        # 1. MRZ Checksum Validation
        mrz_result = MRZValidator.validate_mrz_checksums(raw_mrz)
        for f in mrz_result.get("flags", []):
            all_flags.append(f)
            critical_violations.append(f)

        # 2. Date Sanity Logic
        dob_val = fields.get("date_of_birth", {}).get("value")
        issue_val = fields.get("date_of_issue", {}).get("value")
        exp_val = fields.get("date_of_expiry", {}).get("value")
        date_result = DateValidator.validate_dates(dob_val, issue_val, exp_val)
        for f in date_result.get("flags", []):
            all_flags.append(f)
            if "Critical" in f or "EXPIRED" in f:
                critical_violations.append(f)

        # 3. Country Code & Document Number Format
        country_code = fields.get("issuing_country", {}).get("value") or fields.get("nationality", {}).get("value")
        country_result = CodeAndFormatValidator.validate_country_code(country_code)
        if country_result.get("flag"):
            all_flags.append(country_result["flag"])

        doc_num = fields.get("passport_number", {}).get("value") or fields.get("visa_number", {}).get("value") or fields.get("document_number", {}).get("value")
        format_result = CodeAndFormatValidator.validate_document_number_format(doc_type, doc_num)
        for f in format_result.get("flags", []):
            all_flags.append(f)

        # 4. Cross-Zone Consistency (VIZ vs MRZ)
        cross_zone_result = CodeAndFormatValidator.validate_cross_zone_consistency(fields)
        for d in cross_zone_result.get("discrepancies", []):
            all_flags.append(d)
            critical_violations.append(d)

        # 5. Watchlist & Registry Query
        holder_name = fields.get("full_name", {}).get("value") or fields.get("surname", {}).get("value")
        alt_docs = []
        doc_field = fields.get("passport_number") or fields.get("visa_number") or fields.get("document_number")
        if isinstance(doc_field, dict) and doc_field.get("viz_value"):
            alt_docs.append(doc_field["viz_value"])

        watchlist_result = WatchlistService.check_document(
            document_number=doc_num,
            holder_name=holder_name,
            country_code=country_code,
            alt_document_numbers=alt_docs
        )
        for f in watchlist_result.get("flags", []):
            all_flags.append(f)
            if watchlist_result.get("alert_level") == "CRITICAL":
                critical_violations.append(f)

        # Compute composite validation score (0.0 to 1.0, 1.0 = perfect validity)
        penalty = 0.0
        if not mrz_result["is_valid"] and len(raw_mrz) >= 2:
            penalty += 0.35
        if not date_result["is_valid"]:
            penalty += 0.25
        if not country_result["is_valid"] and country_code:
            penalty += 0.15
        if not cross_zone_result["is_consistent"]:
            penalty += 0.30
        if watchlist_result["is_blacklisted"] or watchlist_result["is_person_of_interest"]:
            penalty += 0.50

        validation_score = max(0.0, round(1.0 - penalty, 3))
        is_overall_valid = len(critical_violations) == 0

        return {
            "is_valid": is_overall_valid,
            "validation_score": validation_score,
            "mrz_checks": mrz_result,
            "date_checks": date_result,
            "country_checks": country_result,
            "format_checks": format_result,
            "cross_zone_checks": cross_zone_result,
            "watchlist_checks": watchlist_result,
            "all_flags": all_flags,
            "critical_violations": critical_violations
        }
