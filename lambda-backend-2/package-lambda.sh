#!/bin/bash

# Exit on error
set -e

echo "Installing dependencies..."
cd src
npm install

echo "Creating deployment package..."
zip -r ../function.zip .

echo "Deployment package created successfully!" 