FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y curl
RUN pip install -r requirements.txt
COPY main.py .
COPY data_types/ ./data_types/
COPY utils/ ./utils/

# Ensure Python can find the data_types and utils modules
ENV PYTHONPATH=/app

CMD ["python", "main.py"]