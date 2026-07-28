FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/backend:/app/backend/django-api:/app/backend/ai-engine

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . /app/

# Expose port (Zoho Catalyst injects X_ZOHO_CATALYST_LISTEN_PORT at runtime)
EXPOSE 9000

# Run unified single-process Python server
CMD ["python", "server.py"]
