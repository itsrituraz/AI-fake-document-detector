# Multi-stage Dockerfile for AI-Based Fake Identity & Document Screening System

# ==========================================
# Stage 1: Build React Frontend
# ==========================================
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# ==========================================
# Stage 2: Python Backend & Unified App
# ==========================================
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system dependencies for OpenCV and image libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and data
COPY . .

# Copy built frontend assets from Stage 1 into the container
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Pre-generate synthetic specimens (zero PII)
RUN python scripts/generate_specimens.py

EXPOSE 8000

# Start unified server
CMD ["python", "main.py", "--host", "0.0.0.0", "--port", "8000"]
