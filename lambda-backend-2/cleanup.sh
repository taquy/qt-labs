#!/bin/bash

# Exit on error
set -e

# Default values
STACK_NAME="idea-management-cursor"
ENVIRONMENT="dev"
REGION="ap-southeast-1"  # Singapore region
PACKAGE_BUCKET="idea-management-package-${ENVIRONMENT}"

# Function to check if AWS CLI is installed
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        echo "Error: AWS CLI is not installed. Please install it first."
        exit 1
    fi
}

# Function to check if stack exists
check_stack_exists() {
    if ! aws cloudformation describe-stacks --stack-name ${STACK_NAME} --region ${REGION} &> /dev/null; then
        echo "Stack ${STACK_NAME} does not exist."
        return 1
    fi
    return 0
}

# Function to get stack status
get_stack_status() {
    aws cloudformation describe-stacks \
        --stack-name ${STACK_NAME} \
        --query 'Stacks[0].StackStatus' \
        --output text \
        --region ${REGION}
}

# Function to delete the stack
delete_stack() {
    echo "Deleting CloudFormation stack..."
    aws cloudformation delete-stack \
        --stack-name ${STACK_NAME} \
        --region ${REGION}

    echo "Waiting for stack deletion to complete..."
    aws cloudformation wait stack-delete-complete \
        --stack-name ${STACK_NAME} \
        --region ${REGION}

    echo "Stack deletion completed successfully!"
}

# Function to empty S3 bucket
empty_bucket() {
    local bucket_name=$1
    echo "Emptying S3 bucket: ${bucket_name}"
    
    # Delete all objects in the bucket
    aws s3api delete-objects \
        --bucket ${bucket_name} \
        --delete "$(aws s3api list-object-versions \
            --bucket ${bucket_name} \
            --output json \
            --query '{Objects: [].{Key:Key,VersionId:VersionId}}')" \
        --region ${REGION}
}

# Function to delete S3 bucket
delete_bucket() {
    local bucket_name=$1
    echo "Deleting S3 bucket: ${bucket_name}"
    
    # Delete bucket policy if exists
    aws s3api delete-bucket-policy --bucket ${bucket_name} --region ${REGION} 2>/dev/null || true
    
    # Delete bucket
    aws s3api delete-bucket --bucket ${bucket_name} --region ${REGION}
}

# Function to clean up S3 buckets
cleanup_s3_buckets() {
    # Get all buckets with the prefix
    local buckets=$(aws s3api list-buckets \
        --query "Buckets[?starts_with(Name, 'idea-management')].Name" \
        --output text \
        --region ${REGION})

    for bucket in $buckets; do
        echo "Processing bucket: ${bucket}"
        empty_bucket "${bucket}"
        delete_bucket "${bucket}"
    done
}

# Function to clean up local files
cleanup_local() {
    echo "Cleaning up local files..."
    rm -rf node_modules
    rm -f package-lock.json
    rm -f packaged.yaml
    echo "Local cleanup completed!"
}

# Main execution
echo "Starting cleanup process..."

# Run checks
check_aws_cli

# Check if stack exists
if ! check_stack_exists; then
    echo "Stack ${STACK_NAME} does not exist. Proceeding with S3 bucket cleanup..."
else
    # Confirm stack deletion
    echo "Warning: This will delete the stack ${STACK_NAME} and all its resources."
    echo "This action cannot be undone!"
    read -p "Are you sure you want to continue? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cleanup cancelled."
        exit 1
    fi

    # Delete the stack
    delete_stack
fi

# Clean up S3 buckets
echo "Cleaning up S3 buckets..."
cleanup_s3_buckets

# Clean up local files
cleanup_local

echo "Cleanup process completed!" 