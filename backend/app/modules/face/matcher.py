"""
Biometric Face Matcher & Verification Engine
============================================
Matches document photo against live/selfie image, evaluates similarity
against security thresholds, and generates human-readable verdicts.
"""

from typing import Dict, Any, Optional
import numpy as np
from .detector import FaceDetector
from .embedder import FaceEmbedder
from ..ocr.preprocessor import DocumentPreprocessor


class FaceMatcher:
    """Master face verification coordinator."""

    MATCH_THRESHOLD = 0.65  # Cosine similarity threshold for confirmed match

    @classmethod
    def verify(
        cls,
        document_input,
        selfie_input: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Runs biometric verification between document portrait and selfie.
        If selfie_input is None, only performs document photo extraction.
        Returns:
            {
                "is_matched": bool,
                "similarity_score": float (0.0 - 1.0),
                "similarity_percentage": float (0 - 100%),
                "l2_distance": float,
                "verdict": "MATCH_CONFIRMED" | "MISMATCH_ALERT" | "NO_SELFIE_PROVIDED" | "FACE_NOT_DETECTED",
                "document_face_found": bool,
                "selfie_face_found": bool,
                "flags": List[str],
                "explanation": str,
                "document_face_thumbnail": str,
                "selfie_face_thumbnail": Optional[str]
            }
        """
        doc_img = DocumentPreprocessor.load_image(document_input)
        doc_face = FaceDetector.extract_document_face(doc_img)

        flags = []

        if not doc_face["found"]:
            flags.append("Warning: Could not clearly isolate biometric face in document photo quadrant")

        # If no selfie provided
        if selfie_input is None:
            return {
                "is_matched": True,
                "similarity_score": 1.0,
                "similarity_percentage": 100.0,
                "l2_distance": 0.0,
                "verdict": "NO_SELFIE_PROVIDED",
                "document_face_found": doc_face["found"],
                "selfie_face_found": False,
                "flags": ["Notice: Document screened without live selfie photo verification"],
                "explanation": "No live selfie provided for 1:1 facial biometric matching",
                "document_face_thumbnail": doc_face["thumbnail_base64"],
                "selfie_face_thumbnail": None,
                "document_face_bbox": doc_face["bbox"]
            }

        # Process selfie
        selfie_img = DocumentPreprocessor.load_image(selfie_input)
        selfie_face = FaceDetector.extract_selfie_face(selfie_img)

        if not selfie_face["found"]:
            flags.append("Alert: No human face detected in uploaded selfie image")
        if selfie_face.get("multiple_faces"):
            flags.append(f"Notice: Multiple faces detected in selfie background ({selfie_face.get('face_count')} faces)")

        # Compute embeddings
        doc_emb = FaceEmbedder.extract_embedding(doc_face["crop"])
        selfie_emb = FaceEmbedder.extract_embedding(selfie_face["crop"])

        cosine_sim, l2_dist = FaceEmbedder.compute_similarity(doc_emb, selfie_emb)
        sim_pct = round(cosine_sim * 100, 1)

        is_matched = (cosine_sim >= cls.MATCH_THRESHOLD) and doc_face["found"] and selfie_face["found"]

        if is_matched:
            verdict = "MATCH_CONFIRMED"
            explanation = f"Biometric verification PASSED: Face match confirmed ({sim_pct}% facial embedding similarity)"
        elif not doc_face["found"] or not selfie_face["found"]:
            verdict = "FACE_NOT_DETECTED"
            explanation = "Biometric check INCOMPLETE: Face could not be isolated in one or both images"
        else:
            verdict = "MISMATCH_ALERT"
            flags.append(f"CRITICAL BIOMETRIC MISMATCH: Similarity {sim_pct}% is below required threshold ({cls.MATCH_THRESHOLD * 100:.0f}%)")
            explanation = f"POTENTIAL IMPERSONATION: Live selfie does NOT match document portrait ({sim_pct}% similarity)"

        return {
            "is_matched": is_matched,
            "similarity_score": cosine_sim,
            "similarity_percentage": sim_pct,
            "l2_distance": l2_dist,
            "verdict": verdict,
            "document_face_found": doc_face["found"],
            "selfie_face_found": selfie_face["found"],
            "flags": flags,
            "explanation": explanation,
            "document_face_thumbnail": doc_face["thumbnail_base64"],
            "selfie_face_thumbnail": selfie_face["thumbnail_base64"],
            "document_face_bbox": doc_face["bbox"],
            "selfie_face_bbox": selfie_face["bbox"]
        }
