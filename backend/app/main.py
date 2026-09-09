"""
AI-Based Fake Identity & Document Screening System — FastAPI Application
========================================================================
Main application entrypoint with CORS, static specimen mounts, and API routes.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api.endpoints import router as api_router

app = FastAPI(
    title="AI-Based Fake Identity & Document Screening System API",
    description="Automated border checkpoint document verification, multi-detector forensics, and biometric face matching.",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://border-sentry.vercel.app",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static demo specimen directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
SPECIMENS_DIR = os.path.join(BASE_DIR, "data", "specimens")
if os.path.exists(SPECIMENS_DIR):
    app.mount("/static/specimens", StaticFiles(directory=SPECIMENS_DIR), name="specimens")

# Include API Router
app.include_router(api_router)


@app.get("/")
def root_status():
    return {
        "system": "AI-Based Fake Identity & Document Screening System",
        "status": "OPERATIONAL",
        "version": "1.0.0",
        "docs_url": "/docs",
        "screening_endpoint": "/api/screen"
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "HEALTHY",
        "modules": {
            "module_1_ocr": "ACTIVE",
            "module_2_validation": "ACTIVE",
            "module_3_forensics": "ACTIVE",
            "module_4_biometrics": "ACTIVE"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
