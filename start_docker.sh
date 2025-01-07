#!/bin/bash

# Get the latest commit ID
COMMIT_ID=$(git rev-parse --short HEAD)

# Export the commit ID as an environment variable
export COMMIT_ID

# Build and start the Docker Compose services
docker compose up --build
