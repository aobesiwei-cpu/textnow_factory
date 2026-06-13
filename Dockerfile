FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 5000

# Environment variables
ENV DB_TYPE=sqlite
ENV SQLITE_PATH=/app/data/textnow_factory.db
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Initialize database and start application
RUN python database/init_db.py || true
CMD ["python", "app.py"]
