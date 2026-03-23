# ---- Stage 1: Build frontend ----
FROM node:22-slim AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
# vite outDir '../static' → outputs to /static (one level up)
RUN npm run build

# ---- Stage 2: Runtime ----
FROM python:3.13-slim
WORKDIR /app

# Build tools needed for compiling C extensions (numpy, pandas, etc.) on ARM64
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies before copying app code (better layer cache)
COPY pyproject.toml ./
RUN pip install --no-cache-dir \
    "aiofiles>=24.1.0" \
    "fastapi>=0.135.1" \
    "uvicorn>=0.42.0" \
    "vectorbt>=0.26.2" \
    "yfinance>=0.2.18"

COPY app/ ./app/
COPY main.py ./
COPY --from=frontend-builder /static ./static

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
