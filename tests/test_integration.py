"""
End-to-End Integration Tests
============================
Tests the FastAPI screening endpoint, composite risk calculation,
SQLite persistence, officer decisions, and stats.
"""

import os
import sys
try:
    import pytest
except ImportError:
    pytest = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from fastapi.testclient import TestClient
from app.main import app
from app.database import get_screening_by_id

client = TestClient(app)
SPECIMEN_DIR = os.path.join(BASE_DIR, "data", "specimens")


def test_root_and_health():
    """Verifies API root and health check endpoints."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"
    assert data["modules"]["module_1_ocr"] == "ACTIVE"


def test_authentic_passport_screening_e2e():
    """Authentic passport with matching selfie must yield LOW RISK (Green)."""
    doc_path = os.path.join(SPECIMEN_DIR, "authentic_passport.jpg")
    selfie_path = os.path.join(SPECIMEN_DIR, "selfie_matching_johnson.jpg")

    with open(doc_path, "rb") as f_doc, open(selfie_path, "rb") as f_selfie:
        res = client.post(
            "/api/screen",
            files={
                "document": ("authentic_passport.jpg", f_doc, "image/jpeg"),
                "selfie": ("selfie_matching_johnson.jpg", f_selfie, "image/jpeg")
            }
        )

    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["risk_assessment"]["overall_risk_score"] < 35.0
    assert data["risk_assessment"]["risk_tier"] == "LOW"
    assert data["risk_assessment"]["risk_color"] == "green"
    assert data["screening_id"] is not None

    screening_id = data["screening_id"]
    db_rec = get_screening_by_id(screening_id)
    assert db_rec is not None
    assert db_rec["document_number"] == "P12345678"
    print(f"\n[OK] Authentic Passport E2E Screening: Risk {data['risk_assessment']['overall_risk_score']} ({data['risk_assessment']['risk_tier']})")


def test_tampered_passport_screening_e2e():
    """Photo-spliced passport must yield HIGH RISK (Red)."""
    doc_path = os.path.join(SPECIMEN_DIR, "tampered_passport_photo_spliced.jpg")
    selfie_path = os.path.join(SPECIMEN_DIR, "selfie_matching_johnson.jpg")

    with open(doc_path, "rb") as f_doc, open(selfie_path, "rb") as f_selfie:
        res = client.post(
            "/api/screen",
            files={
                "document": ("tampered_passport_photo_spliced.jpg", f_doc, "image/jpeg"),
                "selfie": ("selfie_matching_johnson.jpg", f_selfie, "image/jpeg")
            }
        )

    assert res.status_code == 200
    data = res.json()
    assert data["risk_assessment"]["overall_risk_score"] >= 70.0
    assert data["risk_assessment"]["risk_tier"] == "HIGH"
    assert data["risk_assessment"]["risk_color"] == "red"
    print(f"\n[OK] Tampered Passport E2E Screening: Risk {data['risk_assessment']['overall_risk_score']} ({data['risk_assessment']['risk_tier']})")


def test_blacklisted_passport_screening_e2e():
    """Interpol blacklisted passport must yield 100 Risk (CRITICAL)."""
    doc_path = os.path.join(SPECIMEN_DIR, "blacklisted_passport.jpg")

    with open(doc_path, "rb") as f_doc:
        res = client.post(
            "/api/screen",
            files={
                "document": ("blacklisted_passport.jpg", f_doc, "image/jpeg")
            }
        )

    assert res.status_code == 200
    data = res.json()
    assert data["risk_assessment"]["overall_risk_score"] == 100.0
    assert data["risk_assessment"]["risk_tier"] == "HIGH"
    assert any("Interpol" in s for s in data["risk_assessment"]["summary_signals"])
    print("\n[OK] Blacklisted Passport E2E Screening: Risk 100.0 (CRITICAL ALERT)")


def test_officer_decision_and_stats():
    """Tests recording officer decisions and retrieving KPI metrics."""
    history = client.get("/api/history?limit=5").json()
    assert len(history) > 0
    test_id = history[0]["id"]

    # Record decision
    dec_res = client.post(
        f"/api/history/{test_id}/decision",
        json={"decision": "APPROVED", "officer_notes": "Supervisor reviewed and approved test specimen."}
    )
    assert dec_res.status_code == 200
    assert dec_res.json()["decision"] == "APPROVED"

    # Verify stats
    stats_res = client.get("/api/stats")
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert stats["total_screenings"] >= 1
    print(f"\n[OK] Decision & Stats Verified: Total Scans = {stats['total_screenings']}")


if __name__ == "__main__":
    test_root_and_health()
    test_authentic_passport_screening_e2e()
    test_tampered_passport_screening_e2e()
    test_blacklisted_passport_screening_e2e()
    test_officer_decision_and_stats()
    print("\n[ALL INTEGRATION TESTS PASSED SUCCESSFULLY!]")
