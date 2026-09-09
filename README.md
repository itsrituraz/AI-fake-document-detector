# 🛡️ AI-Based Fake Identity & Document Screening System

[![Test Suite](https://img.shields.io/badge/pytest-31%20passed-brightgreen.svg)](#testing)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg?logo=react&logoColor=black)](https://reactjs.org)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-v4-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8.svg?logo=opencv&logoColor=white)](https://opencv.org)
[![ICAO Doc 9303](https://img.shields.io/badge/ICAO-Doc%209303%20Standard-blue.svg)](https://www.icao.int)

An automated document screening and biometric verification platform engineered for **border control checkpoints, immigration authorities, and high-security identity verification**.

Manual inspection of travel documents is slow and vulnerable to sophisticated forgeries, photo splicing, date alteration, and fraudulent stamps. This system combines **Computer Vision, Deep Learning OCR, ICAO MRZ Checksum Validation, Error Level Analysis (ELA) Forensics, and 1:1 Biometric Face Matching** into a unified screening engine that computes an explainable **Risk Score (0–100)** to assist—not replace—human border officers.

---

## 📑 Table of Contents
1. [Key Architecture & Modules](#-key-architecture--modules)
2. [Tech Stack](#-tech-stack)
3. [Repository Structure](#-repository-structure)
4. [Quickstart & Installation](#-quickstart--installation)
5. [Running the Application](#-running-the-application)
6. [Synthetic Specimen Dataset](#-synthetic-specimen-dataset)
7. [API Documentation](#-api-documentation)
8. [Testing & Quality Assurance](#-testing--quality-assurance)
9. [Officer Screening Workflow](#-officer-screening-workflow)
10. [Design & Explainable Risk Scoring Engine](#-design--explainable-risk-scoring-engine)

---

## 🔍 Key Architecture & Modules

The platform is structured into four specialized forensic modules coordinated by an integrated risk scoring and decision layer:

```
                  ┌─────────────────────────────────────────────────┐
                  │          Document Upload (Image / PDF)          │
                  │             + Optional Live Selfie              │
                  └───────────────────────┬─────────────────────────┘
                                          │
                  ┌───────────────────────▼─────────────────────────┐
                  │           FastAPI Master Coordinator            │
                  └───────┬───────────────┬─────────────────┬───────┘
                          │               │                 │
             ┌────────────▼─────┐   ┌─────▼──────────┐   ┌──▼───────────────┐
             │ Module 1: OCR &  │   │  Module 2:     │   │ Module 3:        │
             │ Preprocessing    │   │  Validation    │   │ Digital Forensics│
             │                  │   │                │   │                  │
             │ • Hough Deskew   │   │ • ICAO Doc9303 │   │ • ELA Heatmap    │
             │ • EasyOCR Engine │   │   7-3-1 Mod 10 │   │ • Font Anomaly   │
             │ • Field Parser   │   │ • Chronology   │   │ • EXIF Tampering │
             │ • Confidence Sc. │   │ • SLTD DB & PR │   │ • Stamp Template │
             └────────────┬─────┘   └─────┬──────────┘   └──┬───────────────┘
                          │               │                 │
                          └───────────────┼─────────────────┘
                                          │
                            ┌─────────────▼────────────┐
                            │ Module 4: Biometric Face │
                            │ Verification (1:1 Match) │
                            │                          │
                            │ • Haar & Skin Contour    │
                            │ • 128D Spatial Embedding │
                            │ • Cosine Similarity      │
                            └─────────────┬────────────┘
                                          │
                            ┌─────────────▼────────────┐
                            │  Composite Risk Engine   │
                            │  (0-100 Score & Tiers)   │
                            └─────────────┬────────────┘
                                          │
                  ┌───────────────────────┴─────────────────────────┐
                  │                                                 │
        ┌─────────▼────────┐                              ┌─────────▼────────┐
        │  SQLite Audit    │                              │ React + Tailwind │
        │  screenings.db   │                              │ Officer Console  │
        └──────────────────┘                              └──────────────────┘
```

### Module 1: OCR Extraction & Classification
* **Document Auto-Classification:** Automatically detects Document Type (`PASSPORT`, `VISA`, `NATIONAL_ID`) using ICAO MRZ markers (`P<`, `V<`, `I<`) and visual keywords.
* **Hough Deskewing & Adaptive Contrast:** Deskews rotated document scans ($\pm 45^\circ$) using OpenCV Probabilistic Hough Line Transform and enhances contrast via adaptive thresholding.
* **Specialized Field Extractors:** Extracts Document Number, Full Name, Nationality, Date of Birth, Expiration Date, Issuing Authority, and Machine Readable Zone (MRZ) strings.
* **Per-Field Confidence Scoring:** Calculates character confidence metrics ($0.0 - 1.0$) to flag noisy or unreadable text zones.

### Module 2: Document Validation & Watchlists
* **ICAO Doc 9303 Checksum Engine:** Recomputes character-by-character checksums using the standard 7-3-1 repeating weight modulo 10 algorithm over document number, date of birth, expiration date, and master composite string.
* **Chronological Consistency:** Enforces strict logical timelines (`Expiration Date` > `Issue Date` > `Date of Birth`, validates expired credentials, and verifies legal adulthood requirements).
* **ISO 3166-1 Alpha-3 Verification:** Validates issuing nation and nationality against the standardized ISO 3166 country registry.
* **Interpol SLTD & Civil Registry Lookup:** Queries mock Interpol Stolen and Lost Travel Documents (SLTD) registry, revoked visa watchlists, and national issuance databases with OCR character normalization (`O`/`0`, `I`/`1`).

### Module 3: Digital Forensic Tampering Detection
* **Error Level Analysis (ELA):** Recompresses document images at $95\%$ JPEG quality and computes absolute pixel compression differences. Generates an interactive **ColorJet Heatmap** highlighting spliced photo regions and altered text.
* **Typography & Font Consistency Analyzer:** Evaluates baseline alignment deviations ($\Delta y$) and character height variances across text lines to uncover digitally altered dates or numbers inserted with mismatched fonts.
* **EXIF Metadata Forensics:** Scans EXIF tags for digital manipulation signatures (Adobe Photoshop, GIMP, Canva) and flags inconsistencies between capture timestamps and file system timestamps.
* **Circular Consular Stamp Verifier:** Identifies circular seals using Hough Circle transforms, performs multi-scale template correlation against reference consular stamps, and computes HSV color histogram similarity.

### Module 4: Biometric Face Verification
* **Portrait Extraction:** Automatically detects, crops, and normalizes passport/ID photo portraits ($160\times 160$ px) using OpenCV Haar cascades and HSV skin-tone contour morphology.
* **Selfie Comparison (1:1 Matching):** Extracts document and live traveler selfie embeddings into calibrated 128-dimensional spatial-gradient feature vectors.
* **Cosine Similarity & Verdict:** Computes cosine distance ($0.0 - 1.0$), outputting `MATCH` (similarity $\ge 0.70$), `MISMATCH` (similarity $< 0.70$), or `UNVERIFIED` if no selfie was submitted.

### Integration Layer & Risk Engine
* **Composite Weighted Scoring:**
  $$\text{Score} = (0.35 \times \text{Tamper}) + (0.30 \times \text{Validation}) + (0.25 \times \text{Face}) + (0.10 \times \text{OCR})$$
* **Critical Security Overrides:** Stolen document matches, Interpol Red Notices, or extreme photo splicing automatically trigger immediate **HIGH RISK (100/100)** override.
* **Audit Trail Database:** Persists every screening transaction into `screenings.db` (SQLite) with full JSON diagnostic payloads, timestamping, officer verdicts, and review notes.

---

## 🛠️ Tech Stack

| Layer | Technology | Key Libraries / Frameworks |
| :--- | :--- | :--- |
| **Backend** | Python 3.11+ | FastAPI, Uvicorn, Pydantic v2, Pytest |
| **OCR & CV** | Computer Vision / ML | EasyOCR, OpenCV (`cv2`), Pillow, NumPy |
| **Forensics** | Image Forensics | ELA, Hough Circle Transform, SciPy, ExifRead |
| **Biometrics** | Facial Analysis | 128D Spatial Feature Pooling, Cosine Similarity |
| **Database** | Embedded SQL | SQLite3 (Persistent audit log & officer decisions) |
| **Frontend** | React 18+ | Vite, Vanilla CSS + Tailwind CSS v4, Lucide Icons |

---

## 📂 Repository Structure

```
.
├── ARCHITECTURE.md                 # In-depth architectural design & risk engine documentation
├── README.md                       # Master system documentation (this file)
├── requirements.txt                # Python backend dependencies
├── data/
│   ├── reference_stamps/           # Official circular consular seal templates
│   └── specimens/                  # 100% synthetic document specimens & selfies
│       └── manifest.json           # Specimen catalog with expected ground truth
├── scripts/
│   └── generate_specimens.py       # Script to generate realistic synthetic document images
├── backend/
│   └── app/
│       ├── main.py                 # FastAPI application entrypoint & static mounts
│       ├── database.py             # SQLite persistence layer (screenings.db)
│       ├── api/
│       │   ├── coordinator.py      # Multi-module pipeline orchestrator
│       │   └── endpoints.py        # REST API route handlers (/api/screen, etc.)
│       ├── data/
│       │   ├── mock_watchlist.json # Mock Interpol SLTD & Red Notice database
│       │   └── mock_issued_registry.json # Mock government civil issuance registry
│       ├── models/
│       │   └── schemas.py          # Pydantic request/response schemas
│       ├── scoring/
│       │   └── risk_engine.py      # Explainable 0-100 composite risk scoring engine
│       └── modules/
│           ├── ocr/                # Module 1: Deskew, EasyOCR, document parsers
│           ├── validation/         # Module 2: ICAO Doc 9303 checksums, chronology, watchlists
│           ├── forensics/          # Module 3: ELA heatmap, font analyzer, EXIF, stamp matcher
│           └── face/               # Module 4: Portrait detection, 128D embeddings, matcher
├── frontend/
│   ├── package.json                # Vite + React + Tailwind frontend dependencies
│   ├── vite.config.js              # Vite dev server with proxy to backend
│   └── src/
│       ├── main.jsx                # React root
│       ├── App.jsx                 # Border Officer single-page cockpit application
│       ├── index.css               # Modern dark-mode styling tokens & animations
│       └── components/
│           ├── Navbar.jsx          # Top status bar with live backend ping & stats modal toggle
│           ├── UploadZone.jsx      # Drag-and-drop document & selfie uploader + specimen picker
│           ├── RiskGauge.jsx       # Animated circular SVG score gauge with color tiers
│           ├── DocumentViewer.jsx  # Split-screen viewer with interactive ELA Heatmap overlay
│           ├── BiometricsCard.jsx  # 1:1 facial biometric matching visualizer
│           ├── ForensicsCard.jsx   # ELA, font consistency, EXIF, and circular stamp metrics
│           ├── ValidationCard.jsx  # ICAO checksum breakdown, chronology, watchlist hits
│           ├── OcrCard.jsx         # Extracted fields table with confidence badges
│           ├── OfficerDecisionConsole.jsx # Approve / Reject / Escalate decision controls
│           └── HistoryModal.jsx    # Audit trail review log with search & filters
└── tests/
    ├── conftest.py                 # Pytest fixtures & sample image generators
    ├── test_ocr.py                 # OCR extraction & parsing unit tests
    ├── test_validation.py          # ICAO checksum, chronology, and watchlist tests
    ├── test_forensics.py           # ELA, stamp, and font consistency unit tests
    ├── test_face.py                # 1:1 biometric face matching tests
    └── test_integration.py         # End-to-end API screening & SQLite audit log tests
```

---

## 🚀 Quickstart & Installation

### Prerequisites
* **Python**: Version 3.11 or higher (Python 3.11, 3.12, 3.13, 3.14 supported).
* **Node.js**: Version 18.x or higher (with `npm`).
* **Git**: To clone the repository.

### 1. Backend Setup

```bash
# Clone the repository
git clone <repo-url>
cd "AI-Based Fake Identity & Document Screening System"

# (Optional) Create and activate a Python virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install backend dependencies
pip install -r requirements.txt
```

### 2. Frontend Setup

```bash
cd frontend
npm install
cd ..
```

### 3. Generate Synthetic Specimen Dataset

Generate the 100% synthetic travel documents, tampered specimens, and selfies (ensures zero real PII):

```bash
python scripts/generate_specimens.py
```

---

## 🖥️ Running the Application

### Option A: Run Both Servers Concurrently

#### Start Backend (Terminal 1)
```bash
# From workspace root:
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
* Backend API: [http://127.0.0.1:8000](http://127.0.0.1:8000)
* Interactive Swagger Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

#### Start Frontend (Terminal 2)
```bash
# From frontend folder:
cd frontend
npm run dev
```
* Officer Dashboard: [http://localhost:5173](http://localhost:5173)

---

## 🧪 Synthetic Specimen Dataset

All testing documents are **100% synthetic**, procedurally generated using Pillow and OpenCV, containing fictitious names, fake passport numbers, and synthetic face portraits.

| Specimen Filename | Category | Key Characteristics | Expected Tier |
| :--- | :--- | :--- | :---: |
| `authentic_passport.jpg` | Authentic Passport | Genuine US Passport specimen (`Sarah Johnson`), valid MRZ checksums, clean font alignment, authentic seal. | **LOW RISK** (10–25) |
| `tampered_passport_photo_spliced.jpg` | Spliced Photo | Digital photo forgery where traveler photo was pasted over original portrait. Triggers high ELA noise. | **HIGH RISK** (85–100) |
| `tampered_passport_date_altered.jpg` | Altered Expiry Date | Visual expiration date altered to `2032` while MRZ reads `2029`. Triggers cross-zone mismatch & font anomaly. | **HIGH RISK** (75–95) |
| `authentic_visa.jpg` | Authentic Visa | Genuine Schengen Type-C visa specimen (`Robert Chen`) with authentic consular seal and matching MRZ. | **LOW RISK** (10–25) |
| `tampered_visa_fake_stamp.jpg` | Fraudulent Stamp | Visa bearing a fake consular stamp with mismatched diameter and color profile. | **HIGH RISK** (70–90) |
| `blacklisted_passport.jpg` | Stolen Document | Document number `L898902C3` registered in Interpol SLTD database (`Anna Eriksson`). | **HIGH RISK** (100) |
| `selfie_matching_johnson.jpg` | Biometric Match | Traveler selfie matching `authentic_passport.jpg` portrait. | **Cosine Match** ($\ge 0.70$) |
| `selfie_mismatched_person_b.jpg` | Biometric Mismatch | Traveler selfie of an unrelated individual presenting `authentic_passport.jpg`. | **Biometric Alert** ($< 0.70$) |

---

## 📡 API Documentation

### 1. Document Screening (`POST /api/screen`)
Uploads a document image/PDF and optional live selfie for full 4-module forensic screening.

**Request:** `multipart/form-data`
* `document` *(file, required)*: Document image (JPG, PNG) or PDF.
* `selfie` *(file, optional)*: Live camera capture of the traveler.
* `document_type_hint` *(string, optional)*: `PASSPORT`, `VISA`, `NATIONAL_ID`, or `AUTO`.

**Response (Summary):**
```json
{
  "screening_id": 1,
  "timestamp": "2026-09-08T12:38:00.000000Z",
  "document_type": "PASSPORT",
  "document_number": "A12345678",
  "holder_name": "SARAH JOHNSON",
  "risk_assessment": {
    "overall_score": 14.5,
    "risk_tier": "LOW",
    "recommendation": "STANDARD PROCESSING - LOW RISK",
    "critical_flags": []
  },
  "ocr_extraction": {
    "document_type": "PASSPORT",
    "confidence_avg": 0.94,
    "fields": {
      "document_number": { "value": "A12345678", "confidence": 0.98 },
      "surname": { "value": "JOHNSON", "confidence": 0.96 }
    }
  },
  "validation": {
    "overall_valid": true,
    "mrz_validation": { "all_checksums_valid": true },
    "date_validation": { "chronology_valid": true },
    "watchlist_hits": []
  },
  "forensics": {
    "tampering_detected": false,
    "tampering_score": 12.0,
    "ela_analysis": { "tampering_suspected": false, "heatmap_base64": "data:image/jpeg;base64,..." },
    "font_analysis": { "font_anomaly_detected": false },
    "stamp_verification": { "stamp_detected": true, "is_authentic": true }
  },
  "biometrics": {
    "verified": true,
    "similarity_score": 0.88,
    "verdict": "MATCH"
  }
}
```

### 2. Officer Decision (`POST /api/decision/{id}`)
Records the border control officer's final administrative action.

**Request Body:**
```json
{
  "decision": "APPROVED",
  "officer_notes": "All security features and facial biometrics verified successfully."
}
```

### 3. Screening Audit History (`GET /api/history`)
* `limit` *(int, default 50)*: Number of past records to return.
* `risk_filter` *(string, optional)*: Filter by `LOW`, `MEDIUM`, or `HIGH`.

### 4. Dashboard KPIs (`GET /api/stats`)
Returns total volume screened, average risk score, tier breakdown, and approved/rejected statistics.

### 5. Specimen List (`GET /api/specimens`)
Returns catalog of synthetic specimens for 1-click loading directly in the officer dashboard.

---

## 🧪 Testing & Quality Assurance

The system includes an extensive automated test suite covering unit tests for all 4 forensic modules, composite risk scoring logic, and end-to-end integration flows.

Run all tests with:
```bash
python -m pytest tests/ -v
```

### Test Suite Coverage:
* `tests/test_ocr.py`: Document classification, EasyOCR parsing, MRZ extraction, confidence calculation.
* `tests/test_validation.py`: ICAO Doc 9303 checksum computation, date chronology validation, Interpol SLTD lookup.
* `tests/test_forensics.py`: Error Level Analysis discrepancy scoring, circular stamp template matching, font baseline consistency.
* `tests/test_face.py`: Haar cascade portrait extraction, 128D feature embedding, cosine similarity thresholding.
* `tests/test_integration.py`: End-to-end multi-part form upload, risk engine computation, SQLite audit log persistence, officer decision recording.

---

## 👮 Officer Screening Workflow

When operating the border control dashboard at [http://localhost:5173](http://localhost:5173):

1. **Upload or Select a Specimen:**
   * Click **"Load Authentic Passport"** or **"Load Spliced Photo Specimen"** from the preloaded Quick Specimens bar, or drag-and-drop a document scan and traveler selfie.
2. **Execute Automated Scan:**
   * Click **"Run Full AI Screening"**. The master coordinator runs Modules 1–4 concurrently.
3. **Inspect the Risk Gauge:**
   * **LOW RISK (0–30, Emerald):** Document is authentic, ICAO checksums match, face matches selfie.
   * **MEDIUM RISK (31–69, Amber):** Minor inconsistencies, unverified selfie, or slightly low OCR confidence.
   * **HIGH RISK (70–100, Rose):** Forgery detected, Interpol watchlist hit, photo splicing, or biometric mismatch.
4. **Interactive Forensic Inspection:**
   * Toggle **"Forensic ELA Heatmap"** on the Document Viewer to inspect color-coded compression artifacts.
   * Review the **Typography Consistency** card for font size irregularities.
   * Inspect the **Biometrics Card** to review document portrait vs live selfie similarity.
5. **Record Officer Verdict:**
   * Select **"Approve Entry"**, **"Reject Entry"**, or **"Escalate to Secondary Inspection"**.
   * Add optional notes (e.g., *"Referred to fraud unit for physical loupe inspection"*).
   * Submit to permanently record into the SQLite audit ledger (`screenings.db`).

---

## 📐 Design & Explainable Risk Scoring Engine

Unlike black-box classification models, this system produces an **explainable diagnostic audit trail** showing exactly which features contributed to the risk score:

| Dimension | Weight | Primary Factors Evaluated |
| :--- | :---: | :--- |
| **Forensics** | **35%** | ELA compression anomalies, EXIF editing software tags, circular seal template correlation, font baseline deviations. |
| **Validation** | **30%** | ICAO Doc 9303 7-3-1 modulo 10 checksums, date chronology (expiry vs issue vs DOB), Interpol SLTD stolen document hits. |
| **Biometrics** | **25%** | 1:1 Cosine similarity between document portrait and live traveler selfie ($0.70$ decision boundary). |
| **OCR Quality** | **10%** | Mean OCR character confidence across all recognized zones. |

### Critical Override Triggers:
* **Interpol SLTD Stolen Document Hit:** Automatically forces Risk Score $= 100$ and flags `CRITICAL_SECURITY_ALERT: STOLEN DOCUMENT IN INTERPOL SLTD DATABASE`.
* **Interpol Red Notice:** Forces Risk Score $= 100$ and flags `CRITICAL_SECURITY_ALERT: TRAVELER SUBJECT TO ACTIVE INTERPOL RED NOTICE`.
* **Photo Splicing Detected:** High ELA anomaly ratio in document photo area forces Risk Score $\ge 85$.
* **MRZ Checksum Failure:** Checksum mismatch forces Risk Score $\ge 75$.

---

## 🔒 Security & Privacy Notice

* **Synthetic Data Only:** All test documents and biometric faces included in this repository are **100% synthetic** and contain zero Personally Identifiable Information (PII).
* **Air-Gapped Operation:** All OCR, forensics, and biometric computations run locally on the host machine without transmitting sensitive traveler data to external cloud APIs.
* **Tamper-Resistant Auditing:** All screening transactions and officer verdicts are recorded into SQLite with UTC timestamps and immutable inspection parameters.

---

## 📄 License
This project is developed for evaluation and educational purposes as an AI-assisted document screening prototype.
