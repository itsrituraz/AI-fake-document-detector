"""
Watchlist & Issued Registry Lookup Service
==========================================
Checks document number and holder identity against local mock databases:
Interpol Stolen/Lost Travel Documents (SLTD), Watchlists, and Civil Issuance Registries.
Includes border-grade OCR normalization (1/I/L and 0/O/C confusions).
"""

import os
import json
import re
from typing import Dict, Any, List, Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
WATCHLIST_FILE = os.path.join(DATA_DIR, "mock_watchlist.json")
ISSUED_REGISTRY_FILE = os.path.join(DATA_DIR, "mock_issued_registry.json")


class WatchlistService:
    """Queries local mock databases for blacklisted items and valid issuance records."""

    @staticmethod
    def _load_json(file_path: str) -> Dict[str, Any]:
        """Loads JSON file from disk dynamically to support live demo updates."""
        if not os.path.exists(file_path):
            return {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] Error reading database {file_path}: {e}")
            return {}

    @classmethod
    def _normalize_doc_id(cls, doc_id: str) -> str:
        """Standardizes common OCR optical confusions (0/O/C, 1/I/L)."""
        clean = re.sub(r'[^A-Z0-9]', '', doc_id.upper())
        # Replace O/Q/C with 0, I/L with 1 for fuzzy match comparison
        return clean.replace('O', '0').replace('C', '0').replace('I', '1').replace('L', '1')

    @classmethod
    def check_document(
        cls,
        document_number: Optional[str],
        holder_name: Optional[str] = None,
        date_of_birth: Optional[str] = None,
        country_code: Optional[str] = None,
        alt_document_numbers: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Scans watchlist and issuance registry.
        Returns:
            {
                "is_blacklisted": bool,
                "is_person_of_interest": bool,
                "is_registered_issued": bool,
                "alert_level": "CLEAR" | "WARNING" | "CRITICAL",
                "matched_records": List[dict],
                "issuance_record": Optional[dict],
                "flags": List[str]
            }
        """
        watchlist_data = cls._load_json(WATCHLIST_FILE)
        issued_data = cls._load_json(ISSUED_REGISTRY_FILE)

        matched_records = []
        flags = []
        is_blacklisted = False
        is_poi = False

        candidate_docs = set()
        if document_number:
            candidate_docs.add(re.sub(r'[^A-Z0-9]', '', str(document_number).upper()))
        if alt_document_numbers:
            for d in alt_document_numbers:
                if d:
                    candidate_docs.add(re.sub(r'[^A-Z0-9]', '', str(d).upper()))

        clean_name = re.sub(r'[^A-Z\s]', '', str(holder_name).upper()).strip() if holder_name else ""

        # 1. Check Blacklisted Documents (Interpol SLTD)
        blacklisted_docs = watchlist_data.get("blacklisted_documents", [])
        for item in blacklisted_docs:
            item_doc = re.sub(r'[^A-Z0-9]', '', item.get("document_number", "").upper())
            item_norm = cls._normalize_doc_id(item_doc)
            
            for c_doc in candidate_docs:
                c_norm = cls._normalize_doc_id(c_doc)
                if c_doc == item_doc or (len(c_norm) >= 7 and c_norm == item_norm):
                    is_blacklisted = True
                    matched_records.append(item)
                    flags.append(
                        f"CRITICAL WATCHLIST HIT: Document '{item_doc}' flagged as '{item.get('alert_type')}' - {item.get('notes')}"
                    )
                    break

        # 2. Check Persons of Interest (Red Notices, Travel Bans)
        persons = watchlist_data.get("persons_of_interest", [])
        for p in persons:
            p_name = re.sub(r'[^A-Z\s]', '', p.get("full_name", "").upper()).strip()
            # Check subset of words in name
            p_words = set(p_name.split())
            cand_words = set(clean_name.split())
            if p_words and cand_words and (p_words.issubset(cand_words) or cand_words.issubset(p_words)):
                is_poi = True
                matched_records.append(p)
                flags.append(
                    f"CRITICAL PERSON OF INTEREST: Match '{p.get('full_name')}': {p.get('reason')} [Action: {p.get('action_required')}]"
                )

        # 3. Check Issued Registry
        issuance_record = None
        is_registered = False
        issued_records = issued_data.get("records", [])
        for rec in issued_records:
            rec_doc = re.sub(r'[^A-Z0-9]', '', rec.get("document_number", "").upper())
            for c_doc in candidate_docs:
                if c_doc == rec_doc:
                    is_registered = True
                    issuance_record = rec
                    break

        if is_blacklisted or is_poi:
            alert_level = "CRITICAL"
        elif not is_registered and candidate_docs:
            alert_level = "WARNING"
            flags.append(f"Notice: Document number not found in civil issuance registry (unregistered or specimen)")
        else:
            alert_level = "CLEAR"

        return {
            "is_blacklisted": is_blacklisted,
            "is_person_of_interest": is_poi,
            "is_registered_issued": is_registered,
            "alert_level": alert_level,
            "matched_records": matched_records,
            "issuance_record": issuance_record,
            "flags": flags
        }
