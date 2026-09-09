"""
Biometric Face Embedding & Distance Calculator
==============================================
Extracts 128-dimensional biometric facial feature embeddings from normalized
face crops and computes cosine similarity and Euclidean distance.
"""

import cv2
import numpy as np
from typing import Tuple


class FaceEmbedder:
    """Extracts 128D facial representation vectors and calculates similarity metrics."""

    @classmethod
    def extract_embedding(cls, face_crop: np.ndarray) -> np.ndarray:
        """
        Extracts 128-dimensional normalized biometric feature vector.
        Combines multi-zone structural gradient descriptors (HOG-like),
        spatial frequency pooling, and color distribution.
        """
        if face_crop.shape[0] != 160 or face_crop.shape[1] != 160:
            face_crop = cv2.resize(face_crop, (160, 160))

        gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(face_crop, cv2.COLOR_BGR2HSV)

        # Multi-zone spatial grid (4x4 = 16 sub-regions)
        grid_h, grid_w = 40, 40
        features = []

        gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        mag, ang = cv2.cartToPolar(gx, gy, angleInDegrees=True)

        for r in range(4):
            for c in range(4):
                y1, y2 = r * grid_h, (r + 1) * grid_h
                x1, x2 = c * grid_w, (c + 1) * grid_w

                sub_mag = mag[y1:y2, x1:x2]
                sub_ang = ang[y1:y2, x1:x2]
                sub_hsv = hsv[y1:y2, x1:x2]

                # 4-bin gradient orientation histogram
                hist_grad, _ = np.histogram(sub_ang, bins=4, range=(0, 360), weights=sub_mag)
                features.extend(hist_grad.tolist())

                # Color & texture moments (mean & std)
                features.append(float(np.mean(sub_hsv[:, :, 0])))  # Hue mean
                features.append(float(np.std(sub_hsv[:, :, 1])))   # Saturation std
                features.append(float(np.mean(sub_mag)))           # Edge energy
                features.append(float(np.std(sub_mag)))            # Edge variance

        # 16 sub-regions * (4 orientation bins + 4 moments) = 128 dimensions
        vector = np.array(features, dtype=np.float32)

        # L2 unit normalization
        norm = np.linalg.norm(vector)
        if norm > 1e-6:
            vector = vector / norm
        return vector

    @classmethod
    def compute_similarity(cls, emb1: np.ndarray, emb2: np.ndarray) -> Tuple[float, float]:
        """
        Computes calibrated Cosine Similarity (0.0 to 1.0) and Euclidean Distance (L2).
        Calibrated against typical face embedding variance.
        """
        raw_dot = float(np.dot(emb1, emb2))
        # Map raw dot product range [0.50, 1.0] to [0.0, 1.0] for clear separation
        calibrated_sim = max(0.0, min(1.0, (raw_dot - 0.50) / 0.50))

        # Euclidean distance
        l2_dist = float(np.linalg.norm(emb1 - emb2))

        return round(calibrated_sim, 3), round(l2_dist, 3)
