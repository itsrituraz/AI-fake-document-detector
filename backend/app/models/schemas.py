"""
Pydantic API Schemas & Data Transfer Objects
============================================
Defines request and response validation models for FastAPI endpoints.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class OfficerDecisionRequest(BaseModel):
    decision: str = Field(..., description="Verdict: APPROVED, REJECTED, or ESCALATED")
    officer_notes: Optional[str] = Field("", description="Officer audit notes")


class OfficerDecisionResponse(BaseModel):
    success: bool
    screening_id: int
    decision: str
    message: str


class ScreeningListItem(BaseModel):
    id: int
    created_at: str
    document_type: Optional[str] = None
    document_number: Optional[str] = None
    holder_name: Optional[str] = None
    overall_risk_score: float
    risk_tier: str
    decision: str
    officer_notes: str
    has_selfie: int


class DashboardStatsResponse(BaseModel):
    total_screenings: int
    average_risk_score: float
    tier_breakdown: Dict[str, int]
    decision_breakdown: Dict[str, int]
