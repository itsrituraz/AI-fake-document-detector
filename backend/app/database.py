"""
SQLite Persistence & Audit Trail Database
==========================================
Manages screening logs, officer decisions, notes, and metrics persistence.
"""

import os
import sqlite3
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

DB_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "screenings.db")


def get_connection():
    """Returns SQLite connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes SQLite schema if not exists."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS screenings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                document_type TEXT,
                document_number TEXT,
                holder_name TEXT,
                overall_risk_score REAL NOT NULL,
                risk_tier TEXT NOT NULL,
                decision TEXT DEFAULT 'PENDING',
                officer_notes TEXT DEFAULT '',
                has_selfie INTEGER DEFAULT 0,
                report_json TEXT NOT NULL
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_screenings_created ON screenings(created_at DESC);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_screenings_doc_no ON screenings(document_number);")
        conn.commit()


def save_screening(
    document_type: str,
    document_number: str,
    holder_name: str,
    overall_risk_score: float,
    risk_tier: str,
    has_selfie: bool,
    report: Dict[str, Any]
) -> int:
    """Inserts a new screening record into SQLite and returns the inserted ID."""
    now_iso = datetime.now(timezone.utc).isoformat()
    report_serialized = json.dumps(report)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO screenings (
                created_at, document_type, document_number, holder_name,
                overall_risk_score, risk_tier, has_selfie, report_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            now_iso, document_type, document_number, holder_name,
            overall_risk_score, risk_tier, 1 if has_selfie else 0, report_serialized
        ))
        conn.commit()
        return cursor.lastrowid


def get_screenings(limit: int = 50, risk_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves recent screening audit logs."""
    with get_connection() as conn:
        cursor = conn.cursor()
        if risk_filter and risk_filter.upper() in ("LOW", "MEDIUM", "HIGH"):
            cursor.execute("""
                SELECT id, created_at, document_type, document_number, holder_name,
                       overall_risk_score, risk_tier, decision, officer_notes, has_selfie
                FROM screenings
                WHERE risk_tier = ?
                ORDER BY id DESC LIMIT ?;
            """, (risk_filter.upper(), limit))
        else:
            cursor.execute("""
                SELECT id, created_at, document_type, document_number, holder_name,
                       overall_risk_score, risk_tier, decision, officer_notes, has_selfie
                FROM screenings
                ORDER BY id DESC LIMIT ?;
            """, (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_screening_by_id(screening_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves full screening record by ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM screenings WHERE id = ?;", (screening_id,))
        row = cursor.fetchone()
        if not row:
            return None
        res = dict(row)
        res["report"] = json.loads(res["report_json"])
        del res["report_json"]
        return res


def update_decision(screening_id: int, decision: str, officer_notes: str = "") -> bool:
    """Updates border control officer verdict (APPROVED, REJECTED, ESCALATED)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE screenings
            SET decision = ?, officer_notes = ?
            WHERE id = ?;
        """, (decision.upper(), officer_notes, screening_id))
        conn.commit()
        return cursor.rowcount > 0


def get_dashboard_stats() -> Dict[str, Any]:
    """Calculates summary KPIs for the border control dashboard."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*), AVG(overall_risk_score) FROM screenings;")
        total_count, avg_risk = cursor.fetchone()
        total_count = total_count or 0
        avg_risk = round(avg_risk or 0.0, 1)

        cursor.execute("SELECT risk_tier, COUNT(*) FROM screenings GROUP BY risk_tier;")
        tiers = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute("SELECT decision, COUNT(*) FROM screenings GROUP BY decision;")
        decisions = {row[0]: row[1] for row in cursor.fetchall()}

        return {
            "total_screenings": total_count,
            "average_risk_score": avg_risk,
            "tier_breakdown": {
                "low": tiers.get("LOW", 0),
                "medium": tiers.get("MEDIUM", 0),
                "high": tiers.get("HIGH", 0)
            },
            "decision_breakdown": decisions
        }


# Initialize DB immediately upon module load
init_db()
