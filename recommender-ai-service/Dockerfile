FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y \
    libpq-dev gcc g++ \
    && rm -rf /var/lib/apt/lists/*

# Install torch CPU-only first
RUN pip install --no-cache-dir \
    torch==2.3.0+cpu \
    --index-url https://download.pytorch.org/whl/cpu

# Install remaining deps (includes packaging, numpy, etc.)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install faiss after packaging is available
RUN pip install --no-cache-dir faiss-cpu==1.8.0

COPY . .
RUN chmod +x entrypoint.sh
RUN mkdir -p artifacts data

EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]
