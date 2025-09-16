FROM python:3.12-slim

WORKDIR /app

# Install system dependencies first (these change rarely)
RUN apt-get update && apt-get install -y curl

# Copy only requirements first for better layer caching
COPY requirements.txt .

# Use mount cache for pip to speed up builds
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Copy application files
COPY main.py .
COPY data_types/ ./data_types/
COPY utils/ ./utils/
COPY schema/ ./schema/
COPY tools/ ./tools/

# Create notebooks directory for saving notebooks
RUN mkdir -p /app/notebooks

# Ensure Python can find the data_types and utils modules
ENV PYTHONPATH=/app

CMD ["python", "main.py"]