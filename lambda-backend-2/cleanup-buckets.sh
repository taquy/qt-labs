#!/bin/bash

# Exit on error
set -e

# Default values
BUCKET_PREFIX="608495931393-ap-"
REGION="ap-southeast-1"  # Singapore region

# Function to check if AWS CLI is installed
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        echo "Error: AWS CLI is not installed. Please install it first."
        exit 1
    fi
}

# Function to list buckets with prefix
list_buckets() {
    aws s3api list-buckets \
        --query "Buckets[?starts_with(Name, '${BUCKET_PREFIX}')].Name" \
        --output text \
        --region ${REGION} | tr '\t' '\n'
}

# Function to empty bucket
empty_bucket() {
    local bucket_name=$1
    echo "Emptying bucket: ${bucket_name}"
    
    # Check if bucket exists
    if ! aws s3api head-bucket --bucket ${bucket_name} --region ${REGION} 2>/dev/null; then
        echo "Bucket ${bucket_name} does not exist or is not accessible."
        return 1
    fi
    
    # Try multiple methods to empty the bucket
    echo "Attempting to empty bucket: ${bucket_name}"
    
    # Method 1: Delete all objects and versions
    echo "Method 1: Deleting all objects and versions..."
    aws s3api delete-objects \
        --bucket ${bucket_name} \
        --delete "$(aws s3api list-object-versions \
            --bucket ${bucket_name} \
            --output json \
            --query '{Objects: [].{Key:Key,VersionId:VersionId}}' \
            --region ${REGION})" \
        --region ${REGION} 2>/dev/null || true
    
    sleep 2  # Wait for operations to complete
    
    # Method 2: Delete all delete markers
    echo "Method 2: Deleting all delete markers..."
    aws s3api delete-objects \
        --bucket ${bucket_name} \
        --delete "$(aws s3api list-object-versions \
            --bucket ${bucket_name} \
            --output json \
            --query '{Objects: [].{Key:Key,VersionId:VersionId}}' \
            --region ${REGION})" \
        --region ${REGION} 2>/dev/null || true
    
    sleep 2  # Wait for operations to complete
    
    # Method 3: Recursive delete using s3 rm
    echo "Method 3: Recursive delete..."
    aws s3 rm "s3://${bucket_name}" --recursive --region ${REGION} 2>/dev/null || true
    
    sleep 2  # Wait for operations to complete
    
    # Method 4: Delete all objects with pagination
    echo "Method 4: Paginated delete..."
    while true; do
        local objects=$(aws s3api list-object-versions \
            --bucket ${bucket_name} \
            --output json \
            --query '{Objects: [].{Key:Key,VersionId:VersionId}}' \
            --region ${REGION} 2>/dev/null || echo '{"Objects":[]}')
        
        if [ "$(echo $objects | jq -r '.Objects | length')" -eq 0 ]; then
            break
        fi
        
        aws s3api delete-objects \
            --bucket ${bucket_name} \
            --delete "$objects" \
            --region ${REGION} 2>/dev/null || true
        
        sleep 2  # Wait for operations to complete
    done
    
    # Final verification
    local object_count=$(aws s3api list-object-versions \
        --bucket ${bucket_name} \
        --query 'length(Contents)' \
        --output text \
        --region ${REGION} 2>/dev/null || echo "0")
    
    if [ "$object_count" -gt 0 ]; then
        echo "Warning: Bucket ${bucket_name} still contains objects after all deletion attempts."
        return 1
    else
        echo "Bucket ${bucket_name} is now empty."
    fi
}

# Function to delete bucket
delete_bucket() {
    local bucket_name=$1
    echo "Deleting bucket: ${bucket_name}"
    
    # Delete bucket policy if exists
    aws s3api delete-bucket-policy --bucket ${bucket_name} --region ${REGION} 2>/dev/null || true
    
    # Delete bucket
    aws s3api delete-bucket --bucket ${bucket_name} --region ${REGION}
}

# Function to process bucket
process_bucket() {
    local bucket_name=$1
    echo "Processing bucket: ${bucket_name}"
    
    # Empty the bucket
    if ! empty_bucket "${bucket_name}"; then
        echo "Failed to empty bucket: ${bucket_name}"
        return 1
    fi
    
    # Delete the bucket
    delete_bucket "${bucket_name}"
    
    echo "Successfully removed bucket: ${bucket_name}"
}

# Main execution
echo "Starting bucket cleanup process..."

# Run checks
check_aws_cli

# Get the list of buckets
echo "Listing buckets with prefix: ${BUCKET_PREFIX}"
BUCKETS=$(list_buckets)

if [ -z "$BUCKETS" ]; then
    echo "No buckets found with prefix: ${BUCKET_PREFIX}"
    exit 0
fi

# Display buckets that will be deleted
echo "The following buckets will be deleted:"
echo "$BUCKETS" | while read -r bucket; do
    echo "- $bucket"
done

# Confirm deletion
echo "Warning: This will delete all buckets with prefix: ${BUCKET_PREFIX}"
echo "This action cannot be undone!"
read -p "Are you sure you want to continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled."
    exit 1
fi

# Process each bucket
echo "$BUCKETS" | while read -r bucket; do
    process_bucket "${bucket}"
done

echo "Bucket cleanup process completed!" 