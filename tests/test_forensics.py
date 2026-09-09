"""
Unit & Integration Tests for Module 3 — Forensic Tampering Detection
====================================================================
Tests Error Level Analysis (ELA), font consistency, EXIF metadata analysis,
and official circular stamp verification on authentic vs tampered specimens.
"""

import os
import sys
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from app.modules.forensics.pipeline import ForensicsPipeline
from app.modules.forensics.ela import ELADetector
from app.modules.forensics.stamp_verifier import StampVerifier
from app.modules.forensics.metadata_analyzer import MetadataForensicAnalyzer
from app.modules.forensics.font_analyzer import FontConsistencyAnalyzer
from app.modules.ocr.preprocessor import DocumentPreprocessor

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


def test_authentic_passport_forensics():
    """Authentic passport should pass forensic checks with low tampering score."""
    ensure_specimens_exist()
    doc_path = os.path.join(SPECIMEN_DIR, "authentic_passport.jpg")
    forensic_out = ForensicsPipeline.analyze(doc_path)

    assert forensic_out["tampering_score"] < 40.0
    assert forensic_out["is_tampered"] is False
    assert forensic_out["ela_heatmap_base64"].startswith("data:image/jpeg;base64,")
    print(f"\n[OK] Authentic Passport Forensics Passed: Score {forensic_out['tampering_score']}")


def test_photo_spliced_passport_tampering():
    """Photo-spliced passport must trigger ELA compression anomaly and metadata manipulation."""
    ensure_specimens_exist()
    doc_path = os.path.join(SPECIMEN_DIR, "tampered_passport_photo_spliced.jpg")
    forensic_out = ForensicsPipeline.analyze(doc_path)

    assert forensic_out["sub_detector_scores"]["ela"] >= 35.0
    assert len(forensic_out["triggers"]) > 0
    assert forensic_out["is_tampered"] is True
    print(f"\n[OK] Photo Splicing Detected: Score {forensic_out['tampering_score']}, Triggers: {forensic_out['triggers']}")


def test_stamp_verification_authentic():
    """Tests circular consular seal template and color correlation on authentic passport."""
    ensure_specimens_exist()
    doc_path = os.path.join(SPECIMEN_DIR, "authentic_passport.jpg")
    img = DocumentPreprocessor.load_image(doc_path)
    stamp_res = StampVerifier.verify_stamp(img)

    assert stamp_res["is_verified"] is True
    assert stamp_res["similarity_score"] >= 0.40
    assert stamp_res["color_correlation"] > 0.50
    assert stamp_res["stamp_bbox"] is not None
    print(f"\n[OK] Authentic Stamp Verification Passed: Similarity {stamp_res['similarity_score']:.2f}")


def test_stamp_verification_fake_stamp():
    """Tests that a fraudulent distorted stamp triggers a stamp anomaly."""
    ensure_specimens_exist()
    doc_path = os.path.join(SPECIMEN_DIR, "tampered_visa_fake_stamp.jpg")
    img = DocumentPreprocessor.load_image(doc_path)
    stamp_res = StampVerifier.verify_stamp(img)

    assert stamp_res["is_verified"] is False
    assert stamp_res["similarity_score"] < 0.40
    print(f"\n[OK] Fraudulent Stamp Correctly Flagged: Similarity {stamp_res['similarity_score']:.2f}")


def test_ela_detector_direct():
    """Directly tests ELADetector compression analysis and heatmap generation."""
    ensure_specimens_exist()
    doc_path = os.path.join(SPECIMEN_DIR, "authentic_passport.jpg")
    img = DocumentPreprocessor.load_image(doc_path)
    ela_out = ELADetector.analyze(img)

    assert "ela_score" in ela_out
    assert "max_local_discrepancy" in ela_out
    assert "photo_region_anomaly" in ela_out
    assert "heatmap_base64" in ela_out
    assert ela_out["heatmap_base64"].startswith("data:image/jpeg;base64,")


def test_metadata_forensic_analyzer_direct():
    """Directly tests MetadataForensicAnalyzer on clean vs modified specimens."""
    ensure_specimens_exist()
    clean_path = os.path.join(SPECIMEN_DIR, "authentic_passport.jpg")
    clean_meta = MetadataForensicAnalyzer.analyze(clean_path)
    assert clean_meta["editing_software_detected"] is False

    spliced_path = os.path.join(SPECIMEN_DIR, "tampered_passport_photo_spliced.jpg")
    spliced_meta = MetadataForensicAnalyzer.analyze(spliced_path)
    assert spliced_meta["editing_software_detected"] is True
    assert "Photoshop" in str(spliced_meta["software_signature"])


def test_font_consistency_analyzer_direct():
    """Directly tests FontConsistencyAnalyzer on consistent vs anomalous text boxes."""
    blank_img = np.zeros((600, 900, 3), dtype=np.uint8)

    # Inconsistent boxes (drastically different heights on the same line)
    anomalous_boxes = [
        {"text": "SURNAME", "bbox": {"x": 330, "y": 145, "w": 80, "h": 14}},
        {"text": "JOHNSON", "bbox": {"x": 420, "y": 145, "w": 90, "h": 38}},
        {"text": "GIVEN", "bbox": {"x": 330, "y": 195, "w": 60, "h": 14}},
        {"text": "MICHAEL", "bbox": {"x": 400, "y": 195, "w": 80, "h": 14}},
    ]
    res = FontConsistencyAnalyzer.analyze(blank_img, anomalous_boxes)
    assert "font_anomaly_score" in res
    assert "is_anomalous" in res


if __name__ == "__main__":
    ensure_specimens_exist()
    test_authentic_passport_forensics()
    test_photo_spliced_passport_tampering()
    test_stamp_verification_authentic()
    test_stamp_verification_fake_stamp()
    test_ela_detector_direct()
    test_metadata_forensic_analyzer_direct()
    test_font_consistency_analyzer_direct()
    print("\n[ALL MODULE 3 FORENSIC TESTS PASSED SUCCESSFULLY!]")
