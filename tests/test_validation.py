"""
Unit & Integration Tests for Module 2 — Document Validation
===========================================================
Tests ICAO Doc 9303 MRZ checksums, date chronology logic, ISO country codes,
cross-zone consistency, and mock Interpol SLTD / Red Notice watchlist lookups.
"""

import os
import sys
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from app.modules.validation.pipeline import ValidationPipeline
from app.modules.validation.mrz_validator import MRZValidator
from app.modules.validation.date_validator import DateValidator
from app.modules.validation.code_validator import CodeAndFormatValidator
from app.modules.validation.watchlist import WatchlistService
from app.modules.ocr.pipeline import OCRPipeline

SPECIMEN_DIR = os.path.join(BASE_DIR, "data", "specimens")


def ensure_specimens_exist():
    """Ensures synthetic specimens exist before running tests."""
    doc_path = os.path.join(SPECIMEN_DIR, "authentic_passport.jpg")
    if not os.path.exists(doc_path):
        import subprocess
        gen_script = os.path.join(BASE_DIR, "scripts", "generate_specimens.py")
        subprocess.run([sys.executable, gen_script], check=True)


def setup_module():
    ensure_specimens_exist()


def test_mrz_checksum_calculation():
    """Verifies standard ICAO 7-3-1 check digit calculation on test vectors."""
    # Test vector: Document number 'L898902C3'
    data = "L898902C3"
    check = MRZValidator.calculate_check_digit(data)
    assert check.isdigit()

    # Complete valid TD3 MRZ lines (44 characters each)
    line1 = "P<UTOJOHNSON<<MICHAEL<DAVID<<<<<<<<<<<<<<<<<"
    line2 = "P123456789UTO8506151M3006302<<<<<<<<<<<<<<<0"
    assert len(line1) == 44
    assert len(line2) == 44

    result = MRZValidator.validate_mrz_checksums([line1, line2])
    assert result["is_valid"] is True
    assert result["passed_checks"] == 4
    assert result["total_checks"] == 4
    assert result["check_digits"]["document_number"]["valid"] is True
    assert result["check_digits"]["date_of_birth"]["valid"] is True
    assert result["check_digits"]["date_of_expiry"]["valid"] is True
    assert result["check_digits"]["composite"]["valid"] is True
    print("\n[OK] Valid MRZ Checksums Passed: 4/4 check digits match")


def test_mrz_checksum_tampered_detection():
    """Verifies that an altered character in the MRZ triggers checksum violation."""
    # Altered document number (P12345679 instead of P12345678) but keeping old check digit 9
    line1 = "P<UTOJOHNSON<<MICHAEL<DAVID<<<<<<<<<<<<<<<<<"
    line2 = "P123456799UTO8506151M3006302<<<<<<<<<<<<<<<0"

    result = MRZValidator.validate_mrz_checksums([line1, line2])
    assert result["is_valid"] is False
    assert result["check_digits"]["document_number"]["valid"] is False
    assert len(result["flags"]) > 0
    print(f"\n[OK] Altered MRZ Checksum Detected: {result['flags']}")


def test_date_logic_sanities_valid():
    """Verifies chronological date logic on valid ISO, written, and MRZ dates."""
    # Valid ISO dates
    res1 = DateValidator.validate_dates(dob_str="1985-06-15", issue_str="2020-07-01", expiry_str="2030-06-30")
    assert res1["is_valid"] is True
    assert res1["is_expired"] is False
    assert res1["holder_age_years"] >= 35

    # Valid MRZ 6-digit YYMMDD dates
    res2 = DateValidator.validate_dates(dob_str="850615", issue_str="200701", expiry_str="300630")
    assert res2["is_valid"] is True
    assert res2["is_expired"] is False
    assert res2["parsed_dates"]["date_of_expiry"] == "2030-06-30"
    print("\n[OK] Valid Date Logic Passed (ISO and MRZ YYMMDD)")


def test_date_logic_sanities_invalid():
    """Verifies date validator catches expired documents and chronological inversions."""
    # Invalid: Expiry before issue date
    bad_res = DateValidator.validate_dates(dob_str="1985-06-15", issue_str="2025-07-01", expiry_str="2020-06-30")
    assert bad_res["is_valid"] is False
    assert any("before or equal to issue date" in f for f in bad_res["flags"])

    # Expired document
    expired_res = DateValidator.validate_dates(dob_str="1985-06-15", issue_str="2010-01-01", expiry_str="2020-01-01")
    assert expired_res["is_expired"] is True
    assert expired_res["is_valid"] is False
    assert any("DOCUMENT IS EXPIRED" in f for f in expired_res["flags"])

    # Future date of birth
    future_dob_res = DateValidator.validate_dates(dob_str="2099-01-01")
    assert future_dob_res["is_valid"] is False
    assert any("future" in f.lower() for f in future_dob_res["flags"])
    print("\n[OK] Date Logic Inversions and Expirations Correctly Flagged")


def test_code_and_format_validator():
    """Verifies country code validation and cross-zone consistency checks."""
    # Valid country codes
    assert CodeAndFormatValidator.validate_country_code("USA")["is_valid"] is True
    assert CodeAndFormatValidator.validate_country_code("UTO")["is_valid"] is True

    # Invalid country code
    assert CodeAndFormatValidator.validate_country_code("ZZZ")["is_valid"] is False

    # Cross-zone consistency: matching vs mismatching
    matching_fields = {
        "surname": {"value": "JOHNSON", "viz_value": "JOHNSON"},
        "date_of_expiry": {"value": "2030-06-30", "viz_value": "30 JUN 2030"}
    }
    match_res = CodeAndFormatValidator.validate_cross_zone_consistency(matching_fields)
    assert match_res["is_consistent"] is True

    mismatch_fields = {
        "surname": {"value": "JOHNSON", "viz_value": "SMITH"},
        "date_of_expiry": {"value": "2029-06-30", "viz_value": "30 JUN 2032"}
    }
    mismatch_res = CodeAndFormatValidator.validate_cross_zone_consistency(mismatch_fields)
    assert mismatch_res["is_consistent"] is False
    assert len(mismatch_res["discrepancies"]) >= 2
    print("\n[OK] Code and Cross-Zone Format Validation Passed")


def test_watchlist_service_direct():
    """Directly tests mock Interpol SLTD stolen document database and Red Notice search."""
    # Stolen document match
    stolen_res = WatchlistService.check_document(document_number="L898902C3", holder_name="ANNA ERIKSSON")
    assert stolen_res["is_blacklisted"] is True
    assert stolen_res["alert_level"] == "CRITICAL"
    assert len(stolen_res["flags"]) > 0

    # Clean document
    clean_res = WatchlistService.check_document(document_number="P12345678", holder_name="MICHAEL JOHNSON")
    assert clean_res["is_blacklisted"] is False
    assert clean_res["alert_level"] == "CLEAR"
    print("\n[OK] Watchlist Direct Lookups Passed (SLTD Stolen Doc & Clean)")


def test_validation_pipeline_direct():
    """Tests ValidationPipeline using a decoupled structured OCR data payload."""
    mock_ocr = {
        "classification": {"document_type": "passport"},
        "fields": {
            "document_number": {"value": "P12345678", "confidence": 0.98},
            "surname": {"value": "JOHNSON", "viz_value": "JOHNSON", "confidence": 0.95},
            "given_names": {"value": "MICHAEL DAVID", "viz_value": "MICHAEL DAVID", "confidence": 0.95},
            "nationality": {"value": "UTO", "confidence": 0.95},
            "date_of_birth": {"value": "1985-06-15", "confidence": 0.95},
            "date_of_issue": {"value": "2020-07-01", "confidence": 0.95},
            "date_of_expiry": {"value": "2030-06-30", "viz_value": "30 JUN 2030", "confidence": 0.95},
        },
        "raw_mrz": [
            "P<UTOJOHNSON<<MICHAEL<DAVID<<<<<<<<<<<<<<<<<",
            "P123456789UTO8506151M3006302<<<<<<<<<<<<<<<0"
        ]
    }
    val_res = ValidationPipeline.validate(mock_ocr)
    assert val_res["is_valid"] is True
    assert val_res["validation_score"] >= 0.90
    assert val_res["watchlist_checks"]["is_blacklisted"] is False
    print(f"\n[OK] Validation Pipeline Direct Passed: Score {val_res['validation_score']}")


def test_authentic_passport_validation():
    """Runs full validation pipeline on authentic specimen passport."""
    ensure_specimens_exist()
    doc_path = os.path.join(SPECIMEN_DIR, "authentic_passport.jpg")
    ocr_out = OCRPipeline.process_document(doc_path)
    val_out = ValidationPipeline.validate(ocr_out)

    assert val_out["is_valid"] is True
    assert val_out["validation_score"] >= 0.85
    assert val_out["watchlist_checks"]["is_blacklisted"] is False
    print(f"\n[OK] Authentic Passport Validation: Score {val_out['validation_score']}")


def test_blacklisted_passport_detection():
    """Tests that blacklisted passport (L898902C3) triggers critical Interpol alert."""
    ensure_specimens_exist()
    doc_path = os.path.join(SPECIMEN_DIR, "blacklisted_passport.jpg")
    ocr_out = OCRPipeline.process_document(doc_path)
    val_out = ValidationPipeline.validate(ocr_out)

    assert val_out["watchlist_checks"]["is_blacklisted"] is True
    assert val_out["watchlist_checks"]["alert_level"] == "CRITICAL"
    assert len(val_out["critical_violations"]) > 0
    print(f"\n[OK] Blacklisted Passport Alert Triggered: {val_out['critical_violations']}")


if __name__ == "__main__":
    ensure_specimens_exist()
    test_mrz_checksum_calculation()
    test_mrz_checksum_tampered_detection()
    test_date_logic_sanities_valid()
    test_date_logic_sanities_invalid()
    test_code_and_format_validator()
    test_watchlist_service_direct()
    test_validation_pipeline_direct()
    test_authentic_passport_validation()
    test_blacklisted_passport_detection()
    print("\n[ALL MODULE 2 VALIDATION TESTS PASSED SUCCESSFULLY!]")
