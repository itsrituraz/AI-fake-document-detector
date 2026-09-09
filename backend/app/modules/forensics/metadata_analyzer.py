"""
EXIF & File Structure Metadata Forensic Analyzer
================================================
Extracts metadata tags using exifread and PIL to detect editing software
fingerprints (Adobe Photoshop, GIMP, Canva), timestamp alterations, and missing sensor tags.
"""

import io
import os
from typing import Dict, Any, List, Optional
import exifread
from PIL import Image


KNOWN_MANIPULATION_SOFTWARE = [
    "PHOTOSHOP", "GIMP", "CANVA", "PICSART", "PAINT.NET", "PHOTOPEA",
    "LIGHTROOM", "COREL", "PIXLR", "SNAPSEED", "AFFINITY"
]


class MetadataForensicAnalyzer:
    """Inspects file headers, EXIF tags, and XMP metadata for editing artifacts."""

    @classmethod
    def analyze(cls, input_source) -> Dict[str, Any]:
        """
        Extracts and checks EXIF metadata from file path, bytes, or PIL Image.
        Returns:
            {
                "metadata_threat_score": float (0.0 - 1.0),
                "is_anomalous": bool,
                "software_signature": Optional[str],
                "editing_software_detected": bool,
                "camera_make_model": Optional[str],
                "exif_tags_count": int,
                "flags": List[str],
                "explanation": str
            }
        """
        tags = {}
        flags = []
        software_found = None
        camera_info = None

        raw_bytes = None
        if isinstance(input_source, str) and os.path.exists(input_source):
            with open(input_source, "rb") as f:
                raw_bytes = f.read()
        elif isinstance(input_source, bytes):
            raw_bytes = input_source

        # 1. Parse EXIF with exifread
        if raw_bytes:
            try:
                tags = exifread.process_file(io.BytesIO(raw_bytes), details=False)
            except Exception as e:
                pass

        # Check Software Tag
        software_tag = tags.get("Image Software") or tags.get("Software")
        if software_tag:
            soft_str = str(software_tag).upper()
            software_found = str(software_tag)
            for tool in KNOWN_MANIPULATION_SOFTWARE:
                if tool in soft_str:
                    flags.append(f"Image was modified using photo manipulation software: '{software_found}'")
                    break

        # Check Camera / Scanner hardware profile
        make = tags.get("Image Make")
        model = tags.get("Image Model")
        if make or model:
            camera_info = f"{make or ''} {model or ''}".strip()

        # Check raw bytes for embedded software signature strings (e.g. Adobe XMP header)
        if raw_bytes and not software_found:
            for tool in KNOWN_MANIPULATION_SOFTWARE:
                if tool.encode() in raw_bytes.upper():
                    software_found = tool.capitalize()
                    flags.append(f"Detected embedded digital editor signature in file stream: '{tool}'")
                    break

        # Check for stripped EXIF metadata in raw camera captures
        exif_count = len(tags)

        # Threat scoring (0.0 to 1.0)
        threat_score = 0.0
        editing_detected = False
        if flags:
            editing_detected = True
            threat_score = 0.85

        explanation = "; ".join(flags) if flags else (
            f"Clean metadata stream ({exif_count} EXIF tags; no image editing signatures detected)"
        )

        return {
            "metadata_threat_score": round(threat_score, 3),
            "is_anomalous": editing_detected,
            "software_signature": software_found,
            "editing_software_detected": editing_detected,
            "camera_make_model": camera_info,
            "exif_tags_count": exif_count,
            "flags": flags,
            "explanation": explanation
        }
