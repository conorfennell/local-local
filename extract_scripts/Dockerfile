# Use an official Python runtime as the base image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies with retry logic
RUN set -eux; \
    apt-get update -y; \
    for i in $(seq 1 3); do \
        apt-get install -y \
        build-essential \
        libpq-dev \
        && break || { \
            if [ $i -lt 3 ]; then \
                sleep 5; \
                apt-get update -y; \
            else \
                false; \
            fi \
        }; \
    done; \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . /app/

# Set environment variables
# Prevents Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

# Expose port 8000
EXPOSE 8000

# Run the schedule extraction script
CMD ["python", "schedule_extraction.py"]