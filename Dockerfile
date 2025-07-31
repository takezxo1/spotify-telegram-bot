FROM python:3.11-slim

# Install system dependencies including ffmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements_github.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY *.py ./

# Create temp directory
RUN mkdir -p /tmp/telegram_bot_downloads

# Run the bot
CMD ["python", "main.py"]