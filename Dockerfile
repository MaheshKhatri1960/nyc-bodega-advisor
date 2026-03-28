FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (critical for image and audio)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files (ignoring via .dockerignore)
COPY . .

# Explicitly use the PORT environment variable provided by Cloud Run
ENV PORT 8080
EXPOSE 8080

# The CMD should be one line for reliability in Docker
CMD ["streamlit", "run", "app.py", "--server.port", "8080", "--server.address", "0.0.0.0"]
