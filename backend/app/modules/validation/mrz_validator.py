"""
ICAO Doc 9303 MRZ Checksum Validator
====================================
Implements official ICAO Doc 9303 check digit algorithms using 7-3-1 weight pattern.
Validates individual field checksums and the master composite checksum.
"""

from typing import Dict, Any, List, Optional


class MRZValidator:
    """Validates Machine Readable Zone check digits according to ICAO Doc 9303."""

    WEIGHTS = [7, 3, 1]

    @classmethod
    def calculate_check_digit(cls, data: str) -> str:
        """Calculates ICAO 7-3-1 modulo 10 check digit for an alphanumeric string."""
        total = 0
        for i, char in enumerate(data):
            char_upper = char.upper()
            if char_upper.isdigit():
                val = int(char_upper)
            elif 'A' <= char_upper <= 'Z':
                val = ord(char_upper) - ord('A') + 10
            elif char_upper in ('<', ' ', ''):
                val = 0
            else:
                val = 0
            total += val * cls.WEIGHTS[i % 3]
        return str(total % 10)

    @classmethod
    def validate_mrz_checksums(cls, mrz_lines: List[str]) -> Dict[str, Any]:
        """
        Validates check digits for TD3 (passports, 2x44) and MRV (visas, 2x44/2x36).
        Returns:
            {
                "is_valid": bool,
                "passed_checks": int,
                "total_checks": int,
                "check_digits": {
                    "document_number": {"expected": str, "computed": str, "valid": bool},
                    "date_of_birth": {"expected": str, "computed": str, "valid": bool},
                    "date_of_expiry": {"expected": str, "computed": str, "valid": bool},
                    "composite": {"expected": str, "computed": str, "valid": bool}
                },
                "flags": [str]
            }
        """
        if not mrz_lines or len(mrz_lines) < 2:
            return {
                "is_valid": False,
                "passed_checks": 0,
                "total_checks": 0,
                "check_digits": {},
                "flags": ["No valid 2-line MRZ detected to perform check digit validation"]
            }

        line2 = mrz_lines[1].replace(' ', '').upper()
        if len(line2) < 28:
            return {
                "is_valid": False,
                "passed_checks": 0,
                "total_checks": 0,
                "check_digits": {},
                "flags": [f"MRZ line 2 is truncated ({len(line2)} chars, expected >= 28)"]
            }

        checks = {}
        flags = []

        # 1. Document Number check digit (chars 0-9 data, char 9 is check digit)
        doc_num_data = line2[0:9]
        doc_num_expected = line2[9] if len(line2) > 9 else ""
        doc_num_computed = cls.calculate_check_digit(doc_num_data)
        doc_valid = (doc_num_expected == doc_num_computed)
        checks["document_number"] = {
            "expected": doc_num_expected,
            "computed": doc_num_computed,
            "valid": doc_valid,
            "data": doc_num_data.replace('<', '')
        }
        if not doc_valid:
            flags.append(f"Document number MRZ checksum mismatch: expected '{doc_num_expected}', computed '{doc_num_computed}'")

        # 2. Date of Birth check digit (chars 13-19 data, char 19 is check digit)
        if len(line2) >= 20:
            dob_data = line2[13:19]
            dob_expected = line2[19]
            dob_computed = cls.calculate_check_digit(dob_data)
            dob_valid = (dob_expected == dob_computed)
            checks["date_of_birth"] = {
                "expected": dob_expected,
                "computed": dob_computed,
                "valid": dob_valid,
                "data": dob_data
            }
            if not dob_valid:
                flags.append(f"Date of birth MRZ checksum mismatch: expected '{dob_expected}', computed '{dob_computed}'")

        # 3. Expiration Date check digit (chars 21-27 data, char 27 is check digit)
        if len(line2) >= 28:
            exp_data = line2[21:27]
            exp_expected = line2[27]
            exp_computed = cls.calculate_check_digit(exp_data)
            exp_valid = (exp_expected == exp_computed)
            checks["date_of_expiry"] = {
                "expected": exp_expected,
                "computed": exp_computed,
                "valid": exp_valid,
                "data": exp_data
            }
            if not exp_valid:
                flags.append(f"Expiry date MRZ checksum mismatch: expected '{exp_expected}', computed '{exp_computed}'")

        # 4. Composite check digit (TD3 44 chars)
        if len(line2) >= 44:
            comp_expected = line2[43]
            # Standard ICAO TD3 composite covers: line2[0:10] + line2[13:20] + line2[21:43]
            comp_data = line2[0:10] + line2[13:20] + line2[21:43]
            comp_computed = cls.calculate_check_digit(comp_data)
            comp_valid = (comp_expected == comp_computed)
            checks["composite"] = {
                "expected": comp_expected,
                "computed": comp_computed,
                "valid": comp_valid
            }
            if not comp_valid:
                flags.append(f"Master composite MRZ checksum mismatch: expected '{comp_expected}', computed '{comp_computed}'")

        passed_count = sum(1 for c in checks.values() if c["valid"])
        total_count = len(checks)
        overall_valid = (passed_count == total_count and total_count > 0)

        return {
            "is_valid": overall_valid,
            "passed_checks": passed_count,
            "total_checks": total_count,
            "check_digits": checks,
            "flags": flags
        }
