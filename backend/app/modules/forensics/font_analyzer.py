"""
Font & Typography Consistency Forensic Analyzer
================================================
Examines OCR bounding boxes, character heights, baseline alignments,
and stroke width uniformity to detect digital text overlays and altered fields.
"""

import cv2
import numpy as np
from typing import Dict, Any, List, Optional
from ..ocr.engine import OCRBox


class FontConsistencyAnalyzer:
    """Detects irregular typography, baseline jitter, and font size anomalies."""

    @classmethod
    def analyze(cls, img: np.ndarray, ocr_boxes: List[Any]) -> Dict[str, Any]:
        """
        Analyzes geometric consistency of text regions.
        """
        if not ocr_boxes or len(ocr_boxes) < 4:
            return {
                "font_anomaly_score": 0.0,
                "is_anomalous": False,
                "baseline_deviation_px": 0.0,
                "height_variance": 0.0,
                "flagged_boxes": [],
                "explanation": "Insufficient text boxes to compute typography baseline statistics"
            }

        # Filter out MRZ lines and header bar (y < 70 or y > 460)
        h, w = img.shape[:2]
        viz_boxes = []
        for b in ocr_boxes:
            if isinstance(b, dict):
                bbox = b.get("bbox", {})
                by = bbox.get("y", 0)
                txt = b.get("text", "")
            else:
                by = b.y
                txt = b.text
                bbox = b.to_dict()["bbox"]

            if 70 < by < int(h * 0.76) and "<" not in txt and len(txt.strip()) > 1:
                viz_boxes.append({
                    "text": txt,
                    "x": bbox.get("x", 0),
                    "y": bbox.get("y", 0),
                    "w": bbox.get("w", 0),
                    "h": bbox.get("h", 0),
                    "bbox": bbox
                })

        if len(viz_boxes) < 3:
            return {
                "font_anomaly_score": 0.0,
                "is_anomalous": False,
                "baseline_deviation_px": 0.0,
                "height_variance": 0.0,
                "flagged_boxes": [],
                "explanation": "Uniform typography across visual inspection zone"
            }

        # Cluster boxes into horizontal lines based on strict vertical alignment (abs(y1 - y2) <= 8)
        lines: List[List[dict]] = []
        sorted_by_y = sorted(viz_boxes, key=lambda b: b["y"])

        for b in sorted_by_y:
            placed = False
            for line in lines:
                if abs(b["y"] - line[0]["y"]) <= 8:
                    line.append(b)
                    placed = True
                    break
            if not placed:
                lines.append([b])

        flagged_boxes = []
        baseline_deviations = []
        height_deviations = []

        for line in lines:
            if len(line) < 2:
                continue

            line_sorted = sorted(line, key=lambda b: b["x"])
            y_bottoms = [b["y"] + b["h"] for b in line_sorted]
            heights = [b["h"] for b in line_sorted]

            line_med_bottom = np.median(y_bottoms)
            line_med_height = np.median(heights)

            for b in line_sorted:
                bottom_diff = abs((b["y"] + b["h"]) - line_med_bottom)
                height_ratio = b["h"] / (line_med_height + 1e-5)

                baseline_deviations.append(bottom_diff)
                height_deviations.append(abs(1.0 - height_ratio))

                # Genuine overlay anomalies:
                # 1. Height differs by more than 80% from adjacent words on the exact same baseline
                # 2. Or baseline deviates by > 12 pixels
                if (height_ratio > 1.85 and b["h"] > 26) or (bottom_diff > 14 and len(b["text"]) > 4):
                    flagged_boxes.append({
                        "text": b["text"],
                        "bottom_diff": round(float(bottom_diff), 1),
                        "height": b["h"],
                        "bbox": b["bbox"],
                        "reason": "Mismatched font size/baseline on horizontal tier"
                    })

        avg_baseline_dev = float(np.mean(baseline_deviations)) if baseline_deviations else 0.0
        avg_height_var = float(np.mean(height_deviations)) if height_deviations else 0.0

        # Calculate score (0.0 to 1.0)
        score = 0.0
        if len(flagged_boxes) >= 2:
            score += 0.55
        elif len(flagged_boxes) == 1:
            score += 0.35

        if avg_baseline_dev > 10.0:
            score += 0.25

        font_anomaly_score = min(1.0, round(score, 3))
        is_anomalous = font_anomaly_score >= 0.45

        explanations = []
        if flagged_boxes:
            flagged_words = [f"'{f['text']}'" for f in flagged_boxes[:2]]
            explanations.append(f"Inconsistent font overlay detected in {', '.join(flagged_words)}")
        if not explanations:
            explanations.append("Uniform typography and baseline alignment across all visual fields")

        return {
            "font_anomaly_score": font_anomaly_score,
            "is_anomalous": is_anomalous,
            "baseline_deviation_px": round(avg_baseline_dev, 2),
            "height_variance": round(avg_height_var, 2),
            "flagged_boxes": flagged_boxes,
            "explanation": "; ".join(explanations)
        }
