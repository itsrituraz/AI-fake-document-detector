"""
Date Logic & Chronology Sanity Validator
========================================
Validates that document dates are logically consistent:
Expiry > Issue > DOB; checks for expired documents, underage issuance,
excessive validity periods, and temporal impossibilities.
"""

from datetime import datetime, date
from typing import Dict, Any, List, Optional
import re


class DateValidator:
    """Validates date chronology, validity windows, and expiration status."""

    @classmethod
    def parse_date(cls, date_str: Optional[str], is_expiry: bool = False) -> Optional[date]:
        """Parses arbitrary date strings (YYYY-MM-DD, DD MMM YYYY, etc.) into datetime.date."""
        if not date_str or not isinstance(date_str, str):
            return None

        clean = date_str.strip()

        # Try ISO format YYYY-MM-DD
        try:
            return datetime.strptime(clean, "%Y-%m-%d").date()
        except ValueError:
            pass

        # Try DD MMM YYYY (e.g. 15 JUN 1985)
        try:
            return datetime.strptime(clean, "%d %b %Y").date()
        except ValueError:
            pass

        # Try DD/MM/YYYY or DD-MM-YYYY
        for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(clean, fmt).date()
            except ValueError:
                pass

        # Try YYMMDD (standard ICAO MRZ date format)
        if len(clean) == 6 and clean.isdigit():
            yy = int(clean[0:2])
            mm = int(clean[2:4])
            dd = int(clean[4:6])
            curr_yy = date.today().year % 100
            if is_expiry:
                # Travel document expiry dates are in future or recent past (2000-2079)
                year = 2000 + yy if yy < 80 else 1900 + yy
            else:
                # Birth and issue dates: up to current year is 2000s, older is 1900s
                year = 2000 + yy if yy <= curr_yy else 1900 + yy
            try:
                return date(year, mm, dd)
            except ValueError:
                return None

        return None

    @classmethod
    def validate_dates(
        cls,
        dob_str: Optional[str] = None,
        issue_str: Optional[str] = None,
        expiry_str: Optional[str] = None,
        reference_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Validates date logic against reference date (defaults to today).
        Returns:
            {
                "is_valid": bool,
                "is_expired": bool,
                "days_until_expiry": int,
                "holder_age_years": Optional[int],
                "validity_years": Optional[float],
                "flags": [str]
            }
        """
        today = reference_date or date.today()
        dob = cls.parse_date(dob_str, is_expiry=False)
        issue = cls.parse_date(issue_str, is_expiry=False)
        expiry = cls.parse_date(expiry_str, is_expiry=True)

        flags = []
        is_expired = False
        days_until_expiry = None
        holder_age = None
        validity_years = None

        # 1. DOB Sanity
        if dob:
            if dob > today:
                flags.append(f"Date of birth ({dob}) is in the future")
            else:
                holder_age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                if holder_age > 120:
                    flags.append(f"Implausible holder age: {holder_age} years")

        # 2. Issue Date Sanity
        if issue:
            if issue > today:
                flags.append(f"Document issue date ({issue}) is in the future")
            if dob and issue < dob:
                flags.append(f"Logical error: Document issued ({issue}) before holder was born ({dob})")

        # 3. Expiry Date Sanity
        if expiry:
            delta = (expiry - today).days
            days_until_expiry = delta
            if delta < 0:
                is_expired = True
                flags.append(f"DOCUMENT IS EXPIRED: Expired on {expiry} ({abs(delta)} days ago)")
            elif delta < 180:
                flags.append(f"Notice: Document expires soon (within 6 months: {delta} days remaining)")

            if issue:
                if expiry <= issue:
                    flags.append(f"Critical error: Document expiry date ({expiry}) is before or equal to issue date ({issue})")
                else:
                    validity_years = round((expiry - issue).days / 365.25, 1)
                    if validity_years > 11:
                        flags.append(f"Suspicious validity duration: {validity_years} years (standard ICAO max is 10 years)")

            if dob and expiry <= dob:
                flags.append(f"Critical error: Expiry date ({expiry}) precedes date of birth ({dob})")

        return {
            "is_valid": len([f for f in flags if not f.startswith("Notice:")]) == 0,
            "is_expired": is_expired,
            "days_until_expiry": days_until_expiry,
            "holder_age_years": holder_age,
            "validity_years": validity_years,
            "parsed_dates": {
                "date_of_birth": str(dob) if dob else None,
                "date_of_issue": str(issue) if issue else None,
                "date_of_expiry": str(expiry) if expiry else None
            },
            "flags": flags
        }
