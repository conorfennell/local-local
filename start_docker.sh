#!/bin/bash

# Get the latest commit ID
COMMIT_ID=$(git rev-parse --short HEAD)

# Build and start the Docker Compose services with the commit ID as an environment variable
docker compose up --build -e COMMIT_ID=$COMMIT_ID
