FROM python:3.11-slim

# Install system dependencies required for OpenCV, etc.
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install them separately for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user (optional but good practice)
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Copy backend files
COPY ./backend /app/backend

# Environment variables
ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
