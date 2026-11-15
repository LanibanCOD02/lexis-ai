FROM python:3.10-slim

WORKDIR /app

# Install system dependencies required for FAISS and PyMuPDF
RUN apt-get update && apt-get install -y \
    build-essential \
    libmupdf-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production

# Expose port
EXPOSE 8000

# Run the FastAPI application using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
