#!/bin/bash

# Exit on error
set -e

# Build the base image
echo "Building base image..."
docker build -t qtstocks-base:latest -f Dockerfile.base .

echo "Base image built successfully!"
echo "You can now build development or production images using:"
echo "  - docker build -t qtstocks-dev -f Dockerfile.dev ."
echo "  - docker build -t qtstocks-prod -f Dockerfile ." 