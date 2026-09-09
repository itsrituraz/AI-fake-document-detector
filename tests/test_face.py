"""
Unit & Integration Tests for Module 4 — Biometric Face Verification
===================================================================
Tests face detection, 128D embedding extraction, similarity metrics,
and 1:1 matching across authentic, mismatched, missing face, and document-only inputs.
"""

import os
import sys
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from app.modules.face.matcher import FaceMatcher
from app.modules.face.detector import FaceDetector
from app.modules.face.embedder import FaceEmbedder
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


def test_matching_face_verification():
    """Matching selfie and passport photo should pass with MATCH_CONFIRMED."""
    ensure_specimens_exist()
    doc_path = os.path.join(SPECIMEN_DIR, "authentic_passport.jpg")
    selfie_path = os.path.join(SPECIMEN_DIR, "selfie_matching_johnson.jpg")

    result = FaceMatcher.verify(doc_path, selfie_path)

    assert result["is_matched"] is True
    assert result["verdict"] == "MATCH_CONFIRMED"
    assert result["similarity_percentage"] >= 65.0
    assert result["document_face_found"] is True
    assert result["selfie_face_found"] is True
    assert result["document_face_thumbnail"].startswith("data:image/jpeg;base64,")
    assert result["selfie_face_thumbnail"].startswith("data:image/jpeg;base64,")
    print(f"\n[OK] Matching Face Verification Passed: {result['similarity_percentage']}% ({result['verdict']})")


def test_mismatched_face_verification():
    """Non-matching selfie and passport photo should trigger MISMATCH_ALERT."""
    ensure_specimens_exist()
    doc_path = os.path.join(SPECIMEN_DIR, "authentic_passport.jpg")
    selfie_path = os.path.join(SPECIMEN_DIR, "selfie_mismatched_person_b.jpg")

    result = FaceMatcher.verify(doc_path, selfie_path)

    assert result["is_matched"] is False
    assert result["verdict"] == "MISMATCH_ALERT"
    assert len(result["flags"]) > 0
    assert result["similarity_percentage"] < FaceMatcher.MATCH_THRESHOLD * 100
    print(f"\n[OK] Mismatch Alert Triggered: {result['similarity_percentage']}% ({result['verdict']})")


def test_document_only_verification():
    """Document screening without selfie returns NO_SELFIE_PROVIDED gracefully."""
    ensure_specimens_exist()
    doc_path = os.path.join(SPECIMEN_DIR, "authentic_passport.jpg")
    result = FaceMatcher.verify(doc_path, selfie_input=None)

    assert result["verdict"] == "NO_SELFIE_PROVIDED"
    assert result["document_face_found"] is True
    assert result["selfie_face_found"] is False
    assert result["selfie_face_thumbnail"] is None
    print("\n[OK] Document-Only Screening (No Selfie) Handled Gracefully")


def test_face_not_detected_verification():
    """Screening with image lacking a face returns FACE_NOT_DETECTED."""
    ensure_specimens_exist()
    doc_path = os.path.join(SPECIMEN_DIR, "authentic_passport.jpg")
    blank_selfie = np.zeros((400, 400, 3), dtype=np.uint8)

    result = FaceMatcher.verify(doc_path, blank_selfie)

    assert result["is_matched"] is False
    assert result["verdict"] == "FACE_NOT_DETECTED"
    assert result["selfie_face_found"] is False
    print("\n[OK] Missing Face Handled Gracefully: FACE_NOT_DETECTED")


def test_face_embedder_128d_properties():
    """Verifies that FaceEmbedder outputs normalized 128D vectors."""
    dummy_crop = np.random.randint(50, 200, (160, 160, 3), dtype=np.uint8)
    emb = FaceEmbedder.extract_embedding(dummy_crop)

    assert isinstance(emb, np.ndarray)
    assert emb.shape == (128,)
    assert emb.dtype == np.float32
    # Unit normalization check
    assert np.isclose(np.linalg.norm(emb), 1.0, atol=1e-4)


def test_face_similarity_calibration():
    """Verifies similarity metrics: identical faces yield 1.0 similarity and 0 L2 distance."""
    dummy_crop = np.random.randint(50, 200, (160, 160, 3), dtype=np.uint8)
    emb1 = FaceEmbedder.extract_embedding(dummy_crop)
    emb2 = emb1.copy()

    sim, l2 = FaceEmbedder.compute_similarity(emb1, emb2)
    assert sim == 1.0
    assert l2 == 0.0


def test_face_detector_crops():
    """Tests FaceDetector on authentic passport and selfie crops."""
    ensure_specimens_exist()
    doc_path = os.path.join(SPECIMEN_DIR, "authentic_passport.jpg")
    doc_img = DocumentPreprocessor.load_image(doc_path)
    face_res = FaceDetector.extract_document_face(doc_img)

    assert face_res["found"] is True
    assert face_res["crop"].shape == (160, 160, 3)
    assert "x" in face_res["bbox"] and "w" in face_res["bbox"]
    assert face_res["thumbnail_base64"].startswith("data:image/jpeg;base64,")


if __name__ == "__main__":
    ensure_specimens_exist()
    test_matching_face_verification()
    test_mismatched_face_verification()
    test_document_only_verification()
    test_face_not_detected_verification()
    test_face_embedder_128d_properties()
    test_face_similarity_calibration()
    test_face_detector_crops()
    print("\n[ALL MODULE 4 FACE VERIFICATION TESTS PASSED SUCCESSFULLY!]")
