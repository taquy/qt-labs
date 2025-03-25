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

# Function to check if npm is installed
check_npm() {
    if ! command -v npm &> /dev/null; then
        echo "Error: npm is not installed. Please install it first."
        exit 1
    fi
}

# Function to check if template.yaml exists
check_template() {
    if [ ! -f "template.yaml" ]; then
        echo "Error: template.yaml not found in the current directory."
        exit 1
    fi
}

# Function to create S3 bucket for packaging
create_package_bucket() {
    if ! aws s3 ls "s3://${PACKAGE_BUCKET}" --region ${REGION} 2>/dev/null; then
        echo "Creating S3 bucket for packaging: ${PACKAGE_BUCKET}"
        aws s3 mb "s3://${PACKAGE_BUCKET}" --region ${REGION}
        aws s3api put-bucket-versioning --bucket ${PACKAGE_BUCKET} --versioning-configuration Status=Enabled --region ${REGION}
    fi
}

# Function to install dependencies
install_dependencies() {
    echo "Installing dependencies..."
    npm install
}

# Function to package the application
package_application() {
    echo "Packaging application..."
    sam package \
        --template-file template.yaml \
        --output-template-file packaged.yaml \
        --s3-bucket ${PACKAGE_BUCKET} \
        --region ${REGION}
}

# Function to deploy the stack
deploy_stack() {
    echo "Deploying CloudFormation stack..."
    sam deploy \
        --template-file packaged.yaml \
        --stack-name ${STACK_NAME} \
        --capabilities CAPABILITY_IAM \
        --parameter-overrides EnvironmentName=${ENVIRONMENT} \
        --region ${REGION}

    # Get the stack status
    STACK_STATUS=$(aws cloudformation describe-stacks \
        --stack-name ${STACK_NAME} \
        --query 'Stacks[0].StackStatus' \
        --output text \
        --region ${REGION})

    if [ "$STACK_STATUS" = "CREATE_COMPLETE" ]; then
        echo "Stack deployment completed successfully!"
        
        # Get and display the outputs
        echo "Stack outputs:"
        aws cloudformation describe-stacks \
            --stack-name ${STACK_NAME} \
            --query 'Stacks[0].Outputs' \
            --output table \
            --region ${REGION}
    else
        echo "Stack deployment failed with status: ${STACK_STATUS}"
        exit 1
    fi
}

# Main execution
echo "Starting deployment process..."

# Run checks
check_aws_cli
check_npm
check_template

# Create package bucket if it doesn't exist
create_package_bucket

# Install dependencies
install_dependencies

# Package the application
package_application

# Deploy the stack
deploy_stack

echo "Deployment process completed!" 