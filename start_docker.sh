#!/bin/bash

# Get the latest commit ID
COMMIT_ID=$(git rev-parse --short HEAD)

# Create an .env file with the commit ID
echo "COMMIT_ID=$COMMIT_ID" > .env

# Build and start the Docker Compose services using the .env file
docker compose --env-file .env up --build
