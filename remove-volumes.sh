#!/bin/bash

# Script to remove all volumes created by the ELK docker-compose project

set -e

echo "Removing volumes created by docker-compose..."

# Get the project name (directory name by default)
PROJECT_NAME=$(basename "$(pwd)")

# Remove volumes using docker-compose
docker-compose down -v

echo "All volumes have been removed successfully."
