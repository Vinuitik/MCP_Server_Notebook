FROM python:3.11-slim

WORKDIR /app

# Copy only requirements first for better layer caching
COPY requirements.txt .

# Use mount cache for pip to speed up builds
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Copy the agent application
COPY agent.py .
COPY .env .

EXPOSE 8001

CMD ["python", "agent.py"]
