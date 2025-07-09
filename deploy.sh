#!/bin/bash

# Exit on error
set -e

echo "Starting deployment process..."

# Run tests
echo "Running tests..."
python -m pytest

# Build Docker image
echo "Building Docker image..."
docker build -t formulas:latest .

# Run Docker container
echo "Starting Docker container..."
docker-compose up -d

echo "Deployment completed successfully!"
echo "API is available at http://localhost:8000"
echo "API documentation is available at http://localhost:8000/docs" 