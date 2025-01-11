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

# Check for podman
if podman info > /dev/null 2>&1; then
    echo "Using podman compose"
    podman compose --env-file .env up --build
else
    # If podman isn't available, check for docker
    if ! docker info > /dev/null 2>&1; then
        echo "Neither podman nor docker is running. Please install/start one of them and try again."
        exit 1
    fi
    # Use buildkit and cache options for faster builds
    export DOCKER_BUILDKIT=1
    export COMPOSE_DOCKER_CLI_BUILD=1
    docker compose --env-file .env up --build --build-arg BUILDKIT_INLINE_CACHE=1
fi
