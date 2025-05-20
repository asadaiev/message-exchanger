#!/bin/bash
set -e

echo "Building Docker images..."
docker-compose build

echo "Starting containers..."
docker-compose up -d

echo "Waiting for server to be ready..."
while ! nc -z localhost 8082; do
  sleep 0.5
done

echo "Running tests..."
pytest -s -v tests/test_client_tests.py --disable-warnings

echo "Stopping containers..."
docker-compose down

echo "Done!"
