"""
Biometric Face Detection and Cropping Engine
============================================
Locates, aligns, and crops biometric portraits from travel documents
and live camera/selfie captures, generating normalized face thumbnails.
Supports both deep cascade classifiers and skin-tone oval morphology.
"""

import os
import cv2
import numpy as np
import base64
from typing import Dict, Any, Tuple, Optional, List


class FaceDetector:
    """Detects and extracts normalized face portraits from documents and selfies."""

    _cascade = None

    @classmethod
    def get_cascade(cls):
        """Loads frontal face Haar cascade classifier."""
        if cls._cascade is None:
            cascade_path = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
            if os.path.exists(cascade_path):
                cls._cascade = cv2.CascadeClassifier(cascade_path)
        return cls._cascade

    @classmethod
    def detect_faces(cls, img: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detects faces in BGR image using Haar cascade with skin-tone contour fallback.
        Returns list of bounding boxes (x, y, w, h).
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cascade = cls.get_cascade()
        candidates = []

        if cascade is not None:
            faces = cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=3,
                minSize=(40, 40)
            )
            if len(faces) > 0:
                return [tuple(f) for f in faces]

        # Fallback: Skin-tone HSV contour morphology (reliable for specimen portraits & IDs)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, (0, 15, 50), (35, 230, 255))
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            area = cv2.contourArea(c)
            if area > 1200:
                x, y, w, h = cv2.boundingRect(c)
                aspect = float(h) / float(w + 1e-5)
                # Face ovals typically have aspect ratio between 1.0 and 2.0
                if 0.9 <= aspect <= 2.2 and w > 40 and h > 40:
                    candidates.append((x, y, w, h))

        if candidates:
            # Sort by area descending
            candidates.sort(key=lambda b: b[2] * b[3], reverse=True)
            return candidates

        return []

    @classmethod
    def extract_document_face(cls, doc_img: np.ndarray) -> Dict[str, Any]:
        """
        Locates and crops the ID photo from the document.
        Standard ICAO photo quadrant: left ~4% to 38%, vertical ~14% to 75%.
        """
        h, w = doc_img.shape[:2]
        quad_x, quad_y = int(w * 0.02), int(h * 0.12)
        quad_w, quad_h = int(w * 0.40), int(h * 0.65)
        quad_crop = doc_img[quad_y:quad_y + quad_h, quad_x:quad_x + quad_w]

        faces = cls.detect_faces(quad_crop)
        if faces:
            fx, fy, fw, fh = faces[0]
            x1 = max(0, quad_x + fx)
            y1 = max(0, quad_y + fy)
            x2 = min(w, x1 + fw)
            y2 = min(h, y1 + fh)
            crop = doc_img[y1:y2, x1:x2]
            bbox = {"x": int(x1), "y": int(y1), "w": int(x2 - x1), "h": int(y2 - y1)}
            found = True
        else:
            # Standard ICAO photo rectangle crop
            crop = quad_crop
            bbox = {"x": quad_x, "y": quad_y, "w": quad_w, "h": quad_h}
            found = False  # No face detected in photo quadrant

        normalized = cv2.resize(crop, (160, 160), interpolation=cv2.INTER_AREA)
        _, buf = cv2.imencode(".jpg", normalized, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        thumb_base64 = f"data:image/jpeg;base64,{base64.b64encode(buf).decode('utf-8')}"

        return {
            "found": found,
            "crop": normalized,
            "bbox": bbox,
            "thumbnail_base64": thumb_base64
        }

    @classmethod
    def extract_selfie_face(cls, selfie_img: np.ndarray) -> Dict[str, Any]:
        """
        Locates and crops the primary face from a live camera/selfie capture.
        """
        h, w = selfie_img.shape[:2]
        faces = cls.detect_faces(selfie_img)

        if faces:
            multiple_faces = len(faces) > 1
            fx, fy, fw, fh = faces[0]
            pad_w = int(fw * 0.10)
            pad_h = int(fh * 0.10)
            x1 = max(0, fx - pad_w)
            y1 = max(0, fy - pad_h)
            x2 = min(w, fx + fw + pad_w)
            y2 = min(h, fy + fh + pad_h)
            crop = selfie_img[y1:y2, x1:x2]
            bbox = {"x": int(x1), "y": int(y1), "w": int(x2 - x1), "h": int(y2 - y1)}
            found = True
            face_count = len(faces)
        else:
            # Fallback center crop
            cx, cy = w // 2, h // 2
            size = min(w, h) // 2
            x1, y1 = max(0, cx - size), max(0, cy - size)
            x2, y2 = min(w, cx + size), min(h, cy + size)
            crop = selfie_img[y1:y2, x1:x2]
            bbox = {"x": x1, "y": y1, "w": x2 - x1, "h": y2 - y1}
            found = False
            multiple_faces = False
            face_count = 0

        normalized = cv2.resize(crop, (160, 160), interpolation=cv2.INTER_AREA)
        _, buf = cv2.imencode(".jpg", normalized, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        thumb_base64 = f"data:image/jpeg;base64,{base64.b64encode(buf).decode('utf-8')}"

        return {
            "found": found,
            "multiple_faces": multiple_faces,
            "face_count": face_count,
            "crop": normalized,
            "bbox": bbox,
            "thumbnail_base64": thumb_base64
        }
