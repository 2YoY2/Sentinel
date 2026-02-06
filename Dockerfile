# Use an official Python runtime as a parent image
# Slim version reduces the image size (Best Practice)
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (needed for some ML libraries like chromadb native dep)
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
# Adding --no-cache-dir to keep image small
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Environment variables for cache (fixing the permission issue inside docker too)
ENV SENTINEL_CACHE_DIR=/app/cache
ENV HF_HOME=/app/cache/huggingface
ENV SENTENCE_TRANSFORMERS_HOME=/app/cache/sentence_transformers
RUN mkdir -p /app/cache && chmod 777 /app/cache

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the application
# "host 0.0.0.0" allows external access from outside the container
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
