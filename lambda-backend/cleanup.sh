#!/bin/bash

# Make script executable if not already
chmod +x "$0"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "Error: AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if stack name is provided
if [ -z "$1" ]; then
    echo "Usage: ./cleanup.sh <stack-name>"
    exit 1
fi

STACK_NAME=$1

# Get list of deployment buckets associated with the stack
echo "Finding deployment buckets..."
BUCKETS=$(aws s3 ls | grep "$STACK_NAME" | awk '{print $3}')

# Empty and delete any found buckets
if [ ! -z "$BUCKETS" ]; then
    echo "Found the following buckets to clean up:"
    echo "$BUCKETS"
    for bucket in $BUCKETS; do
        echo "Emptying and deleting bucket: $bucket"
        aws s3 rm s3://$bucket --recursive
        aws s3 rb s3://$bucket
    done
fi

# Delete CloudFormation stack
echo "Deleting CloudFormation stack: $STACK_NAME"
aws cloudformation delete-stack --stack-name $STACK_NAME

# Wait for stack deletion to complete
echo "Waiting for stack deletion to complete..."
aws cloudformation wait stack-delete-complete --stack-name $STACK_NAME

# Clean up local deployment artifacts
echo "Cleaning up local deployment artifacts..."
rm -f packaged.yaml
rm -f samconfig.toml 2>/dev/null

echo "Cleanup completed successfully!"