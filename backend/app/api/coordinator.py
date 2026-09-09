"""
Master Screening Coordinator
============================
Integrates all 4 modules (OCR, Validation, Forensics, Face Verification)
and composite risk scoring into an end-to-end screening transaction.
"""

import time
import numpy as np
from typing import Dict, Any, Optional
from ..modules.ocr.pipeline import OCRPipeline
from ..modules.validation.pipeline import ValidationPipeline
from ..modules.forensics.pipeline import ForensicsPipeline
from ..modules.face.matcher import FaceMatcher
from ..scoring.risk_engine import RiskScoringEngine
from ..database import save_screening


class ScreeningCoordinator:
    """Coordinates full screening pipeline and persists audit records."""

    @classmethod
    def run_screening(
        cls,
        document_bytes: bytes,
        selfie_bytes: Optional[bytes] = None,
        document_type_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes end-to-end screening for incoming document and optional live selfie.
        """
        start_time = time.time()

        # 1. Module 1: OCR Extraction & Classification
        ocr_result = OCRPipeline.process_document(document_bytes, user_document_type=document_type_hint)

        # 2. Module 2: Document Validation & Watchlist Lookup
        validation_result = ValidationPipeline.validate(ocr_result)

        # 3. Module 3: Forensic Tampering Detection
        ocr_boxes = ocr_result.get("ocr_boxes", [])
        forensics_result = ForensicsPipeline.analyze(document_bytes, ocr_boxes=ocr_boxes)

        # 4. Module 4: Biometric Face Verification
        face_result = FaceMatcher.verify(document_bytes, selfie_input=selfie_bytes)

        # 5. Integration Layer: Composite Risk Score Calculation
        risk_result = RiskScoringEngine.calculate_risk(
            ocr_result=ocr_result,
            validation_result=validation_result,
            forensics_result=forensics_result,
            face_result=face_result
        )

        total_elapsed_ms = round((time.time() - start_time) * 1000, 1)

        # Assemble full report
        doc_type = ocr_result.get("classification", {}).get("document_type", "passport")
        doc_num = (
            ocr_result.get("fields", {}).get("passport_number", {}).get("value") or
            ocr_result.get("fields", {}).get("visa_number", {}).get("value") or
            ocr_result.get("fields", {}).get("document_number", {}).get("value") or
            "UNKNOWN"
        )
        holder_name = (
            ocr_result.get("fields", {}).get("full_name", {}).get("value") or
            ocr_result.get("fields", {}).get("surname", {}).get("value") or
            "UNKNOWN"
        )

        final_report = {
            "screening_id": None,
            "success": True,
            "total_processing_time_ms": total_elapsed_ms,
            "document_summary": {
                "document_type": doc_type,
                "document_number": doc_num,
                "holder_name": holder_name,
                "dimensions": ocr_result.get("document_info")
            },
            "risk_assessment": risk_result,
            "ocr": ocr_result,
            "validation": validation_result,
            "forensics": forensics_result,
            "biometrics": face_result
        }

        # 6. Save to SQLite database
        try:
            screening_id = save_screening(
                document_type=doc_type,
                document_number=doc_num,
                holder_name=holder_name,
                overall_risk_score=risk_result["overall_risk_score"],
                risk_tier=risk_result["risk_tier"],
                has_selfie=(selfie_bytes is not None),
                report=final_report
            )
            final_report["screening_id"] = screening_id
        except Exception as e:
            print(f"[!] Warning: Could not save screening to database: {e}")
            final_report["screening_id"] = -1

        return final_report
