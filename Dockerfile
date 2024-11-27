# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set working directory 
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ .

# Set environment variables (provided via Secrets)
ENV OPENAI_API_KEY=""
ENV TELEGRAM_BOT_TOKEN=""

# Expose the Flask app port
EXPOSE 5000

# Start the Flask app
CMD ["python", "app.py"]