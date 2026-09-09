"""
Module 3 — Forensic Tampering Detection Pipeline
================================================
Fuses Error Level Analysis (ELA), font consistency, EXIF metadata,
and circular stamp verification into an integrated tampering likelihood score (0-100).
"""

import numpy as np
from typing import Dict, Any, List, Optional
from .ela import ELADetector
from .font_analyzer import FontConsistencyAnalyzer
from .metadata_analyzer import MetadataForensicAnalyzer
from .stamp_verifier import StampVerifier
from ..ocr.preprocessor import DocumentPreprocessor


class ForensicsPipeline:
    """Master tampering detection coordinator uniting multi-detector forensics."""

    @classmethod
    def analyze(
        cls,
        document_input,
        ocr_boxes: Optional[List[Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes full forensic suite.
        Returns:
            {
                "tampering_score": float (0 - 100),
                "is_tampered": bool,
                "confidence": float,
                "sub_detector_scores": {
                    "ela": float,
                    "font": float,
                    "metadata": float,
                    "stamp_anomaly": float
                },
                "triggers": List[str],
                "explanation": str,
                "ela_details": dict,
                "font_details": dict,
                "metadata_details": dict,
                "stamp_details": dict,
                "ela_heatmap_base64": str
            }
        """
        img = DocumentPreprocessor.load_image(document_input)

        # 1. Error Level Analysis (ELA)
        ela_out = ELADetector.analyze(img)

        # 2. Font / Typography Analysis
        font_out = FontConsistencyAnalyzer.analyze(img, ocr_boxes or [])

        # 3. Metadata Forensics
        meta_out = MetadataForensicAnalyzer.analyze(document_input)

        # 4. Stamp / Seal Check
        stamp_out = StampVerifier.verify_stamp(img)
        stamp_anomaly_score = 1.0 - stamp_out["similarity_score"] if not stamp_out["is_verified"] else 0.0

        # 5. Signal Fusion & Trigger Identification
        triggers = []

        if ela_out["is_anomalous"]:
            triggers.append(f"ELA recompression anomaly: {ela_out['explanation']}")

        if font_out["is_anomalous"]:
            triggers.append(f"Typography anomaly: {font_out['explanation']}")

        if meta_out["is_anomalous"]:
            triggers.append(f"Metadata threat: {meta_out['explanation']}")

        if not stamp_out["is_verified"]:
            triggers.append(f"Stamp mismatch: {stamp_out['explanation']}")

        # Weighted composite score (0 - 100)
        # Weights: ELA (35%), Font (25%), Metadata (20%), Stamp (20%)
        composite_ratio = (
            (0.35 * ela_out["ela_score"]) +
            (0.25 * font_out["font_anomaly_score"]) +
            (0.20 * meta_out["metadata_threat_score"]) +
            (0.20 * stamp_anomaly_score)
        )

        # If any strong single detector triggered a critical alert, ensure score exceeds threshold
        if meta_out["editing_software_detected"]:
            composite_ratio = max(composite_ratio, 0.75)
        if ela_out["is_anomalous"]:
            composite_ratio = max(composite_ratio, 0.60)
        if ela_out["photo_region_anomaly"] > 2.2:
            composite_ratio = max(composite_ratio, 0.70)
        if font_out["font_anomaly_score"] > 0.60:
            composite_ratio = max(composite_ratio, 0.65)

        tampering_score = round(min(100.0, composite_ratio * 100), 1)
        is_tampered = tampering_score >= 40.0

        # Human-readable summary
        if triggers:
            explanation = " | ".join(triggers)
        else:
            explanation = "Authentic integrity: No digital splicing, typography variance, or metadata anomalies detected."

        return {
            "tampering_score": tampering_score,
            "is_tampered": is_tampered,
            "confidence": 0.90,
            "sub_detector_scores": {
                "ela": round(ela_out["ela_score"] * 100, 1),
                "font": round(font_out["font_anomaly_score"] * 100, 1),
                "metadata": round(meta_out["metadata_threat_score"] * 100, 1),
                "stamp_anomaly": round(stamp_anomaly_score * 100, 1)
            },
            "triggers": triggers,
            "explanation": explanation,
            "ela_details": ela_out,
            "font_details": font_out,
            "metadata_details": meta_out,
            "stamp_details": stamp_out,
            "ela_heatmap_base64": ela_out["heatmap_base64"]
        }
