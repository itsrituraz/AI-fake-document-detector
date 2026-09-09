"""
Error Level Analysis (ELA) Forensic Detector
============================================
Detects digital image manipulation, photo splicing, and localized edits
by analyzing JPEG compression error differentials across image regions.
"""

import io
import cv2
import numpy as np
import base64
from PIL import Image
from typing import Dict, Any, Tuple


class ELADetector:
    """Error Level Analysis engine to locate compression layer discrepancies."""

    @classmethod
    def analyze(cls, img: np.ndarray, quality: int = 90, scale: int = 15) -> Dict[str, Any]:
        """
        Executes ELA on BGR image.
        Returns:
            {
                "ela_score": float (0.0 - 1.0),
                "is_anomalous": bool,
                "max_local_discrepancy": float,
                "photo_region_anomaly": float,
                "heatmap_base64": str,
                "explanation": str
            }
        """
        h, w = img.shape[:2]

        # 1. Resave at specified JPEG quality in memory
        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        buffer = io.BytesIO()
        pil_img.save(buffer, format="JPEG", quality=quality)
        buffer.seek(0)
        resaved = Image.open(buffer)
        resaved_bgr = cv2.cvtColor(np.array(resaved), cv2.COLOR_RGB2BGR)

        # 2. Compute absolute difference
        diff = cv2.absdiff(img, resaved_bgr)
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

        # 3. Amplify differences for visual inspection
        amplified = cv2.multiply(gray_diff, scale)
        amplified = np.clip(amplified, 0, 255).astype(np.uint8)

        # 4. Regional Anomaly Analysis
        block_size = 32
        block_means = []
        for y in range(0, h - block_size, block_size):
            for x in range(0, w - block_size, block_size):
                block = amplified[y:y + block_size, x:x + block_size]
                block_means.append(np.mean(block))

        overall_mean = float(np.mean(amplified))
        overall_std = float(np.std(amplified))
        max_block_mean = float(np.max(block_means)) if block_means else overall_mean

        discrepancy_ratio = (max_block_mean / (overall_mean + 1e-5)) if overall_mean > 0 else 1.0

        # Inspect Photo Quadrant (left 5-38%, height 14-75%)
        px1, py1 = int(w * 0.03), int(h * 0.14)
        px2, py2 = int(w * 0.38), int(h * 0.75)
        photo_crop = amplified[py1:py2, px1:px2]
        photo_mean = float(np.mean(photo_crop)) if photo_crop.size > 0 else overall_mean
        photo_discrepancy = photo_mean / (overall_mean + 1e-5)

        # Calibrated anomaly scoring
        raw_score = 0.0
        explanations = []

        # Photo anomaly: significantly higher compression error than document background
        if photo_discrepancy > 1.45:
            raw_score += 0.55
            explanations.append(f"High compression discontinuity in ID photo quadrant ({photo_discrepancy:.2f}x background error; indicates photo splicing)")
        elif photo_discrepancy < 0.25 and overall_mean > 6.0:
            raw_score += 0.30
            explanations.append("Abnormal smoothness in photo quadrant compared to background substrate")

        # Global block discrepancy: only if overall mean has sufficient energy
        if discrepancy_ratio > 3.8 and overall_mean > 5.0:
            raw_score += 0.35
            explanations.append(f"Localized recompression spike detected (discrepancy ratio {discrepancy_ratio:.1f}x)")

        if overall_std > 28.0:
            raw_score += 0.20
            explanations.append(f"High global error variance ({overall_std:.1f})")

        ela_score = min(1.0, round(raw_score, 3))
        is_anomalous = ela_score >= 0.40

        if not explanations:
            explanations.append("Uniform error level distribution consistent with single-generation compression")

        # 5. Generate Heatmap Visualization (ColorJet)
        heatmap_color = cv2.applyColorMap(amplified, cv2.COLORMAP_JET)
        blend = cv2.addWeighted(img, 0.55, heatmap_color, 0.45, 0)
        _, buffer_jpg = cv2.imencode(".jpg", blend, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        heatmap_base64 = base64.b64encode(buffer_jpg).decode("utf-8")

        return {
            "ela_score": ela_score,
            "is_anomalous": is_anomalous,
            "max_local_discrepancy": round(discrepancy_ratio, 2),
            "photo_region_anomaly": round(photo_discrepancy, 2),
            "heatmap_base64": f"data:image/jpeg;base64,{heatmap_base64}",
            "explanation": "; ".join(explanations)
        }
