#!/bin/bash

# Get the latest commit details
COMMIT_ID=$(git rev-parse --short HEAD)
COMMIT_TIME=$(git log -1 --format=%cd --date=iso)
COMMIT_MESSAGE=$(git log -1 --format=%s)

# Create an .env file with the commit details
echo "COMMIT_ID=$COMMIT_ID" > .env
echo "COMMIT_TIME=$COMMIT_TIME" >> .env
echo "COMMIT_MESSAGE=$COMMIT_MESSAGE" >> .env

# Build and start the Docker Compose services using the .env file
docker compose --env-file .env up --build
