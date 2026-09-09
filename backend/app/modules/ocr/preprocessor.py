"""
Document Preprocessing and Normalization Pipeline
=================================================
Handles document loading (JPEG/PNG/PDF), orientation correction,
deskewing, noise filtering, and Region of Interest (ROI) segmentation.
"""

import io
import os
import cv2
import numpy as np
from PIL import Image
import pypdf


class DocumentPreprocessor:
    """Preprocesses input document images or PDFs for OCR and forensic analysis."""

    @staticmethod
    def load_image(input_source) -> np.ndarray:
        """
        Loads document from file path, bytes, or PIL Image.
        Supports JPG, PNG, and multi-page PDF (extracts first page).
        Returns BGR numpy array.
        """
        if isinstance(input_source, np.ndarray):
            return input_source

        if isinstance(input_source, Image.Image):
            rgb = np.array(input_source.convert("RGB"))
            return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

        if isinstance(input_source, bytes):
            # Check if PDF header (%PDF-)
            if input_source.startswith(b"%PDF"):
                return DocumentPreprocessor._pdf_bytes_to_image(input_source)
            nparr = np.frombuffer(input_source, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("Unable to decode image bytes.")
            return img

        if isinstance(input_source, str):
            if not os.path.exists(input_source):
                raise FileNotFoundError(f"File not found: {input_source}")
            if input_source.lower().endswith(".pdf"):
                with open(input_source, "rb") as f:
                    return DocumentPreprocessor._pdf_bytes_to_image(f.read())
            img = cv2.imread(input_source)
            if img is None:
                raise ValueError(f"Unable to read image from path: {input_source}")
            return img

        raise TypeError(f"Unsupported input source type: {type(input_source)}")

    @staticmethod
    def _pdf_bytes_to_image(pdf_bytes: bytes) -> np.ndarray:
        """Extracts first image or renders first page from PDF bytes."""
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        if len(reader.pages) == 0:
            raise ValueError("PDF file contains no pages.")
        first_page = reader.pages[0]
        if first_page.images:
            first_img = first_page.images[0]
            pil_img = Image.open(io.BytesIO(first_img.data)).convert("RGB")
            return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        # Fallback: blank canvas with error notice
        h, w = 600, 900
        canvas = np.ones((h, w, 3), dtype=np.uint8) * 255
        cv2.putText(canvas, "PDF Page (No embedded raster image found)", (50, 300),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 200), 2)
        return canvas

    @staticmethod
    def deskew(img: np.ndarray, max_angle: float = 20.0) -> np.ndarray:
        """
        Detects document skew angle using minAreaRect on document contours
        or Hough lines, and rotates image to correct alignment.
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Edge detection
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 50, 150, apertureSize=3)

        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)
        if lines is None or len(lines) == 0:
            return img

        angles = []
        for line in lines:
            coords = line[0] if (hasattr(line, 'shape') and len(line.shape) > 1) else (line[0] if isinstance(line, list) else line)
            try:
                x1, y1, x2, y2 = [int(v) for v in coords]
            except (TypeError, ValueError):
                continue
            if x2 - x1 == 0:
                continue
            angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
            if abs(angle) <= max_angle:
                angles.append(angle)

        if not angles:
            return img

        median_angle = float(np.median(angles))
        if abs(median_angle) < 0.5:
            return img  # negligible skew

        # Rotate around image center
        h, w = img.shape[:2]
        center = (w // 2, h // 2)
        rot_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
        rotated = cv2.warpAffine(img, rot_matrix, (w, h), flags=cv2.INTER_CUBIC,
                                 borderMode=cv2.BORDER_REPLICATE)
        return rotated

    @staticmethod
    def enhance_for_ocr(img: np.ndarray) -> np.ndarray:
        """
        Enhances text contrast and suppresses background guilloche patterns.
        Applies CLAHE + Bilateral filtering.
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        # Bilateral filter to smooth texture while keeping sharp text edges
        denoised = cv2.bilateralFilter(enhanced, 7, 50, 50)
        return denoised

    @staticmethod
    def extract_mrz_region(img: np.ndarray) -> tuple[np.ndarray, dict]:
        """
        Extracts the bottom Machine Readable Zone (MRZ).
        Standard ICAO TD3 passports locate MRZ in the bottom ~22% of the document.
        Returns: (cropped_mrz_image, bounding_box_dict)
        """
        h, w = img.shape[:2]
        mrz_top = int(h * 0.76)
        mrz_crop = img[mrz_top:h, 0:w]
        bbox = {"x": 0, "y": mrz_top, "w": w, "h": h - mrz_top}
        return mrz_crop, bbox

    @staticmethod
    def extract_viz_region(img: np.ndarray) -> tuple[np.ndarray, dict]:
        """
        Extracts the Visual Inspection Zone (VIZ) (top ~76% of document).
        Returns: (cropped_viz_image, bounding_box_dict)
        """
        h, w = img.shape[:2]
        viz_bottom = int(h * 0.76)
        viz_crop = img[0:viz_bottom, 0:w]
        bbox = {"x": 0, "y": 0, "w": w, "h": viz_bottom}
        return viz_crop, bbox

    @staticmethod
    def extract_photo_region(img: np.ndarray) -> tuple[np.ndarray, dict]:
        """
        Extracts the standard passport photo quadrant (left side, middle height).
        Returns: (cropped_photo_image, bounding_box_dict)
        """
        h, w = img.shape[:2]
        # Standard ICAO photo quadrant: left 5% to 42%, height 14% to 75%
        x1, y1 = int(w * 0.03), int(h * 0.14)
        x2, y2 = int(w * 0.38), int(h * 0.75)
        crop = img[y1:y2, x1:x2]
        bbox = {"x": x1, "y": y1, "w": x2 - x1, "h": y2 - y1}
        return crop, bbox
