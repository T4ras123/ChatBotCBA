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

COPY . .


# Environment variables will be provided via docker-compose or docker run
ENV OPENAI_API_KEY=""
ENV TELEGRAM_BOT_TOKEN=""

# Run the bot
CMD ["python", "src/main.py"]