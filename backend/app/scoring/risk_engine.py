"""
Composite Risk Scoring & Decision Recommendation Engine
========================================================
Combines OCR readability, cryptographic format validation, forensic tampering signals,
and biometric face match results into an actionable 0-100 risk score and tier.
"""

from typing import Dict, Any, List


class RiskScoringEngine:
    """Computes overall risk score (0-100) and officer action recommendation."""

    # Weights for risk factors (total = 1.0)
    WEIGHT_TAMPERING = 0.40       # Forensics (ELA, font, EXIF, stamp)
    WEIGHT_BIOMETRICS = 0.30      # Face verification mismatch
    WEIGHT_VALIDATION = 0.20      # MRZ checksums, dates, ISO codes, watchlist
    WEIGHT_OCR = 0.10             # OCR readability & unread fields

    @classmethod
    def calculate_risk(
        cls,
        ocr_result: Dict[str, Any],
        validation_result: Dict[str, Any],
        forensics_result: Dict[str, Any],
        face_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesizes all 4 modules into a composite risk report.
        Returns:
            {
                "overall_risk_score": float (0 - 100),
                "risk_tier": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
                "risk_color": "green" | "amber" | "red",
                "recommendation": str,
                "breakdown": {
                    "tampering_contribution": float,
                    "biometrics_contribution": float,
                    "validation_contribution": float,
                    "ocr_contribution": float
                },
                "summary_signals": List[str]
            }
        """
        # 1. Tampering Risk (0 - 100)
        tamper_raw = float(forensics_result.get("tampering_score", 0.0))

        # 2. Biometric Risk (0 - 100)
        # If no selfie provided, biometric risk is 0 (neutral)
        if face_result.get("verdict") == "NO_SELFIE_PROVIDED":
            face_risk = 0.0
        elif not face_result.get("is_matched"):
            # High penalty for biometric mismatch
            sim = float(face_result.get("similarity_percentage", 0.0))
            face_risk = max(70.0, 100.0 - sim)
        else:
            # Low risk if matched
            sim = float(face_result.get("similarity_percentage", 100.0))
            face_risk = max(0.0, (100.0 - sim) * 0.5)

        # 3. Validation Risk (0 - 100)
        val_score = float(validation_result.get("validation_score", 1.0))
        val_risk = (1.0 - val_score) * 100.0

        # 4. OCR Quality Risk (0 - 100)
        ocr_conf = float(ocr_result.get("overall_ocr_confidence", 0.85))
        ocr_risk = max(0.0, (1.0 - ocr_conf) * 100.0)

        # Weighted calculation
        c_tamper = round(cls.WEIGHT_TAMPERING * tamper_raw, 1)
        c_face = round(cls.WEIGHT_BIOMETRICS * face_risk, 1)
        c_val = round(cls.WEIGHT_VALIDATION * val_risk, 1)
        c_ocr = round(cls.WEIGHT_OCR * ocr_risk, 1)

        raw_composite = c_tamper + c_face + c_val + c_ocr

        # Critical Overrides
        summary_signals = []

        # Check for Watchlist Critical Hit (Interpol SLTD)
        watchlist_checks = validation_result.get("watchlist_checks", {})
        if watchlist_checks.get("is_blacklisted") or watchlist_checks.get("is_person_of_interest"):
            raw_composite = 100.0
            summary_signals.append("CRITICAL: Document or Person matches active Interpol Watchlist / Stolen Document registry")

        # Check for Photo Splicing / Editing Software
        if forensics_result.get("metadata_details", {}).get("editing_software_detected"):
            raw_composite = max(raw_composite, 85.0)
            summary_signals.append("ALERT: Digital image editing software fingerprints detected in document metadata")

        if forensics_result.get("ela_details", {}).get("photo_region_anomaly", 0) > 1.45:
            raw_composite = max(raw_composite, 78.0)
            summary_signals.append("ALERT: Error Level Analysis flags recompression discontinuity in portrait quadrant (photo splicing)")

        # Check for Biometric Mismatch
        if face_result.get("verdict") == "MISMATCH_ALERT":
            raw_composite = max(raw_composite, 75.0)
            summary_signals.append("ALERT: Biometric face verification failed (subject photo does not match document)")

        # Check for MRZ Checksum Failure
        if not validation_result.get("mrz_checks", {}).get("is_valid") and len(ocr_result.get("raw_mrz", [])) >= 2:
            raw_composite = max(raw_composite, 65.0)
            summary_signals.append("WARNING: ICAO Doc 9303 MRZ cryptographic checksum failure")

        # Check for Expired Document
        if validation_result.get("date_checks", {}).get("is_expired"):
            raw_composite = max(raw_composite, 70.0)
            summary_signals.append("WARNING: Travel document has expired")

        overall_risk = round(min(100.0, max(0.0, raw_composite)), 1)

        # Risk Tier and Actionable Recommendations
        if overall_risk >= 70.0:
            risk_tier = "HIGH"
            risk_color = "red"
            recommendation = "REJECT & IMPOUND: High probability of identity fraud or Interpol alert. Immediate supervisor escalation required."
        elif overall_risk >= 30.0:
            risk_tier = "MEDIUM"
            risk_color = "amber"
            recommendation = "REFER TO SECONDARY INSPECTION: Moderate risk indicators detected. Perform physical tactile inspection and manual registry lookup."
        else:
            risk_tier = "LOW"
            risk_color = "green"
            recommendation = "AUTO-APPROVE READY: Document verified authentic, checksums valid, and biometric match confirmed."

        if not summary_signals:
            summary_signals.append("All automated forensic, cryptographic, and biometric screening checks passed within standard thresholds.")

        return {
            "overall_risk_score": overall_risk,
            "risk_tier": risk_tier,
            "risk_color": risk_color,
            "recommendation": recommendation,
            "breakdown": {
                "tampering_contribution": c_tamper,
                "biometrics_contribution": c_face,
                "validation_contribution": c_val,
                "ocr_contribution": c_ocr
            },
            "sub_scores": {
                "tampering_score": tamper_raw,
                "biometrics_risk": face_risk,
                "validation_risk": val_risk,
                "ocr_risk": ocr_risk
            },
            "summary_signals": summary_signals
        }
