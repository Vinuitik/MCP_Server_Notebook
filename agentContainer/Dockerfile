FROM python:3.11-slim

WORKDIR /app

# Copy only requirements first for better layer caching
COPY requirements.txt .

# Use mount cache for pip to speed up builds
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Copy the agent application and configuration
COPY agent.py .
COPY .env .
COPY service-account-key.json .
COPY config/ ./config/
COPY check_container.py .

# Run a quick check to ensure all files are present
RUN python check_container.py

EXPOSE 8001

CMD ["python", "agent.py"]
