#!/bin/bash

# Build and push script for financemanage-finance_backend

echo "Building financemanage-finance_backend:V1..."

# Change to backend directory where the actual code is
cd backend

# Build the Docker image
docker build --no-cache -t 147.79.66.211:3000/docker/financemanage-finance_backend:V1 .

if [ $? -eq 0 ]; then
    echo "Build successful! Pushing to registry..."
    
    # Push the Docker image
    docker push 147.79.66.211:3000/docker/financemanage-finance_backend:V1
    
    if [ $? -eq 0 ]; then
        echo "Successfully pushed financemanage-finance_backend:V1"
    else
        echo "Failed to push financemanage-finance_backend:V1"
        exit 1
    fi
else
    echo "Build failed for financemanage-finance_backend:V1"
    exit 1
fi
