# ── CreatorAE Dockerfile ──────────────────────────────────────────────────────
# Builds a single image that can run either the FastAPI server or the
# Streamlit UI depending on the CMD override at runtime.

FROM python:3.11-slim

# System dependencies for PDF parsing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (better Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project source
COPY . .

# Default: run FastAPI on port 8000
# Override with: docker run ... streamlit run app/ui/streamlit_app.py --server.port 8501
EXPOSE 8000
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
