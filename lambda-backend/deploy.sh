#!/bin/bash

# Exit if any command fails
set -e

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Set variables
STACK_NAME=idea-management-q
REGION="ap-southeast-1"
TEMPLATE_FILE="template.yaml"
ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
S3_BUCKET="${ACCOUNT_ID}-$(echo ${REGION} | cut -d'-' -f1)-$(date +%s)"

echo "Creating S3 bucket for artifacts..."
aws s3 mb s3://${S3_BUCKET} --region ${REGION}

echo "Packaging CloudFormation templates..."
echo "Packaging API Gateway template..."
aws cloudformation package \
    --template-file api-gateway.yaml \
    --s3-bucket ${S3_BUCKET} \
    --output-template-file packaged-api.yaml \
    --region ${REGION}

# Upload the packaged API template to S3
echo "Uploading API Gateway template to S3..."
aws s3 cp packaged-api.yaml s3://${S3_BUCKET}/packaged-api.yaml
# Get the S3 URL for the API Gateway template
S3_API_TEMPLATE="https://${S3_BUCKET}.s3.${REGION}.amazonaws.com/packaged-api.yaml"
# Update the template URL in the main template
sed -i.bak "s|TemplateURL: ./packaged-api.yaml|TemplateURL: ${S3_API_TEMPLATE}|" ${TEMPLATE_FILE}

echo "Packaging main template..."
aws cloudformation package \
    --template-file ${TEMPLATE_FILE} \
    --s3-bucket ${S3_BUCKET} \
    --output-template-file packaged-main.yaml \
    --region ${REGION}

echo "Deploying stack..."
aws cloudformation deploy \
    --template-file packaged-main.yaml \
    --stack-name ${STACK_NAME} \
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND \
    --region ${REGION} \
    --parameter-overrides \
        UserPoolName=${STACK_NAME}-user-pool \
        ApiStageName=dev \
        S3BucketName=${S3_BUCKET}

echo "Deployment complete!