#!/bin/bash
set -e

# Get the latest commit details
COMMIT_ID=$(git rev-parse --short HEAD)
COMMIT_TIME=$(git log -1 --format=%cd --date=iso)
COMMIT_MESSAGE=$(git log -1 --format=%s)

# Create an .env file with the commit details
echo "COMMIT_ID=$COMMIT_ID" > .env
echo "COMMIT_TIME=$COMMIT_TIME" >> .env
echo "COMMIT_MESSAGE=$COMMIT_MESSAGE" >> .env

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build and start the Docker Compose services using the .env file
docker compose --env-file .env up --build
