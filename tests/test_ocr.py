"""
Unit & Integration Tests for Module 1 — OCR Extraction
======================================================
Tests preprocessing, document classification, field extraction,
confidence scoring, and structured JSON output.
"""

import os
import sys
try:
    import pytest
except ImportError:
    pytest = None

# Add backend directory to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from app.modules.ocr.pipeline import OCRPipeline
from app.modules.ocr.preprocessor import DocumentPreprocessor

SPECIMEN_DIR = os.path.join(BASE_DIR, "data", "specimens")


def test_authentic_passport_extraction():
    """Verifies OCR extraction on authentic specimen passport."""
    doc_path = os.path.join(SPECIMEN_DIR, "authentic_passport.jpg")
    assert os.path.exists(doc_path), f"Specimen missing: {doc_path}"

    result = OCRPipeline.process_document(doc_path)

    # 1. Pipeline success & performance
    assert result["success"] is True
    assert result["processing_time_ms"] > 0
    assert result["document_info"]["width"] == 900
    assert result["document_info"]["height"] == 600

    # 2. Classification check
    classification = result["classification"]
    assert classification["document_type"] == "passport"
    assert classification["confidence"] >= 0.8
    assert classification["is_mrz_present"] is True

    # 3. Field extractions
    fields = result["fields"]
    assert "passport_number" in fields
    assert fields["passport_number"]["value"] == "P12345678"
    assert fields["passport_number"]["confidence"] >= 0.7

    assert "surname" in fields
    assert "JOHNSON" in fields["surname"]["value"].upper()

    assert "gender" in fields
    assert fields["gender"]["value"] == "M"

    assert "date_of_birth" in fields
    assert "1985" in fields["date_of_birth"]["value"] or "850615" in str(fields["date_of_birth"])

    assert "date_of_expiry" in fields
    assert "2030" in fields["date_of_expiry"]["value"] or "300630" in str(fields["date_of_expiry"])

    # 4. MRZ Lines
    assert len(result["raw_mrz"]) == 2
    assert "JOHNSON" in result["raw_mrz"][0]
    assert "P12345678" in result["raw_mrz"][1]

    print("\n[OK] Authentic Passport OCR Extraction Passed!")
    print(f"     Classified: {classification['document_type']} ({classification['confidence']})")
    print(f"     Passport No: {fields['passport_number']['value']} (Conf: {fields['passport_number']['confidence']})")
    print(f"     Holder: {fields.get('surname', {}).get('value')}, {fields.get('given_names', {}).get('value')}")


def test_authentic_visa_extraction():
    """Verifies OCR extraction on authentic specimen visa."""
    doc_path = os.path.join(SPECIMEN_DIR, "authentic_visa.jpg")
    assert os.path.exists(doc_path), f"Specimen missing: {doc_path}"

    result = OCRPipeline.process_document(doc_path)

    assert result["success"] is True
    classification = result["classification"]
    assert classification["document_type"] == "visa"
    assert classification["confidence"] >= 0.8

    fields = result["fields"]
    assert "visa_number" in fields
    assert "V10293847" in fields["visa_number"]["value"]

    assert "entries" in fields
    assert "M" in fields["entries"]["value"].upper() or "MULTIPLE" in fields["entries"]["value"].upper()

    assert "stay_duration" in fields
    assert "90" in fields["stay_duration"]["value"]

    print("\n[OK] Authentic Visa OCR Extraction Passed!")
    print(f"     Classified: {classification['document_type']} ({classification['confidence']})")
    print(f"     Visa No: {fields['visa_number']['value']}")
    print(f"     Stay: {fields['stay_duration']['value']}")


def test_user_type_override():
    """Verifies that a manual user selection is honored with validation."""
    doc_path = os.path.join(SPECIMEN_DIR, "authentic_passport.jpg")
    result = OCRPipeline.process_document(doc_path, user_document_type="passport")
    assert result["classification"]["document_type"] == "passport"


if __name__ == "__main__":
    test_authentic_passport_extraction()
    test_authentic_visa_extraction()
    test_user_type_override()
    print("\n[ALL MODULE 1 OCR TESTS PASSED SUCCESSFULLY!]")
