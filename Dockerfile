# Base Python image
FROM python:3.9-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . /app

# Expose ports for both services (FastAPI: 8000, Streamlit: 8501)
EXPOSE 8000
EXPOSE 8501

# The execution command is defined in docker-compose.yml
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
