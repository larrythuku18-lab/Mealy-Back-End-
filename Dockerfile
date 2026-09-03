FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create instance directory for SQLite
RUN mkdir -p instance

EXPOSE 5000

# Run the app (tables are created automatically by create_app on startup)
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
