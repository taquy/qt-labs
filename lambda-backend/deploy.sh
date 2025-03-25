#!/bin/bash

# Exit if any command fails
set -e

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if stack name is provided
if [ -z "$1" ]; then
    echo "Usage: ./deploy.sh <stack-name> [region]"
    echo "Example: ./deploy.sh my-idea-management-stack us-east-1"
    exit 1
fi

# Set variables
STACK_NAME=$1
REGION="${2:-us-east-1}"  # Default to us-east-1 if region not specified
TEMPLATE_FILE="template.yaml"
S3_BUCKET="${STACK_NAME}-artifacts-$(date +%s)"

echo "Creating S3 bucket for artifacts..."
aws s3 mb s3://${S3_BUCKET} --region ${REGION}

echo "Packaging CloudFormation template..."
aws cloudformation package \
    --template-file ${TEMPLATE_FILE} \
    --s3-bucket ${S3_BUCKET} \
    --output-template-file packaged.yaml \
    --region ${REGION}

echo "Deploying CloudFormation stack..."
aws cloudformation deploy \
    --template-file packaged.yaml \
    --stack-name ${STACK_NAME} \
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
    --region ${REGION} \
    --parameter-overrides UserPoolName=${STACK_NAME}-user-pool

# Clean up
echo "Cleaning up temporary files..."
rm -f packaged.yaml

echo "Deployment completed successfully!"
echo "Stack Name: ${STACK_NAME}"
echo "Region: ${REGION}"