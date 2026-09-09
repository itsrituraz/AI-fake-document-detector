"""
FastAPI REST API Endpoints
==========================
Defines all border screening, audit history, officer decision,
metrics, and demo specimen routes.
"""

import os
import json
from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import JSONResponse

from .coordinator import ScreeningCoordinator
from ..database import (
    get_screenings,
    get_screening_by_id,
    update_decision,
    get_dashboard_stats
)
from ..models.schemas import (
    OfficerDecisionRequest,
    OfficerDecisionResponse,
    ScreeningListItem,
    DashboardStatsResponse
)

router = APIRouter(prefix="/api")

SPECIMENS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "data", "specimens"
)


@router.post("/screen")
async def screen_document(
    document: UploadFile = File(..., description="Document image or PDF file"),
    selfie: Optional[UploadFile] = File(None, description="Optional live selfie portrait"),
    document_type: Optional[str] = Form(None, description="Optional document type hint (passport, visa, national_id)")
):
    """
    Primary Border Screening Gateway.
    Accepts document upload and optional selfie, runs the full 4-module AI inspection,
    and returns comprehensive structured JSON report with composite risk score.
    """
    try:
        doc_bytes = await document.read()
        if not doc_bytes or len(doc_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty document payload provided.")

        selfie_bytes = None
        if selfie is not None:
            selfie_bytes = await selfie.read()
            if len(selfie_bytes) == 0:
                selfie_bytes = None

        report = ScreeningCoordinator.run_screening(
            document_bytes=doc_bytes,
            selfie_bytes=selfie_bytes,
            document_type_hint=document_type
        )
        return report

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Screening pipeline error: {str(e)}")


@router.get("/history", response_model=List[ScreeningListItem])
def get_screening_history(
    limit: int = Query(50, ge=1, le=200),
    risk_filter: Optional[str] = Query(None, description="Filter by risk tier: LOW, MEDIUM, HIGH")
):
    """Retrieves chronological audit log of past screenings."""
    return get_screenings(limit=limit, risk_filter=risk_filter)


@router.get("/history/{screening_id}")
def get_screening_details(screening_id: int):
    """Retrieves full screening report by ID including forensic heatmaps and face crops."""
    record = get_screening_by_id(screening_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Screening record #{screening_id} not found.")
    return record


@router.post("/history/{screening_id}/decision", response_model=OfficerDecisionResponse)
def record_officer_decision(screening_id: int, body: OfficerDecisionRequest):
    """Records human border officer verdict (APPROVED, REJECTED, ESCALATED) and notes."""
    valid_decisions = {"APPROVED", "REJECTED", "ESCALATED"}
    if body.decision.upper() not in valid_decisions:
        raise HTTPException(status_code=400, detail=f"Invalid decision '{body.decision}'. Must be one of: {valid_decisions}")

    success = update_decision(screening_id, body.decision, body.officer_notes or "")
    if not success:
        raise HTTPException(status_code=404, detail=f"Screening record #{screening_id} not found.")

    return {
        "success": True,
        "screening_id": screening_id,
        "decision": body.decision.upper(),
        "message": f"Officer decision '{body.decision.upper()}' successfully recorded."
    }


@router.get("/stats", response_model=DashboardStatsResponse)
def get_screening_stats():
    """Returns dashboard KPI statistics (total scans, average risk score, tier breakdown)."""
    return get_dashboard_stats()


@router.get("/specimens")
def get_specimen_presets():
    """Returns list of pre-generated synthetic demo specimens for 1-click loading."""
    manifest_path = os.path.join(SPECIMENS_DIR, "manifest.json")
    if not os.path.exists(manifest_path):
        return {"specimens": []}
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"specimens": [], "error": str(e)}
