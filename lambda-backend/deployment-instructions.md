# Deployment Instructions

This document explains how to deploy the Idea Management System using the provided deployment script.

## Prerequisites

1. AWS CLI installed and configured with appropriate credentials
2. Bash shell environment
3. Appropriate AWS permissions to create:
   - CloudFormation stacks
   - S3 buckets
   - Lambda functions
   - DynamoDB tables
   - Cognito User Pools
   - IAM roles and policies

## How to Deploy

1. Make the deployment script executable:
   ```bash
   chmod +x deploy.sh
   ```

2. Run the deployment script with required parameters:
   ```bash
   ./deploy.sh <stack-name> [region]
   ```
   
   For example:
   ```bash
   ./deploy.sh idea-management-stack us-east-1
   ```

## Script Behavior

The deployment script will:
1. Create an S3 bucket to store deployment artifacts
2. Package the CloudFormation template and upload artifacts to S3
3. Deploy the CloudFormation stack with the specified name
4. Clean up temporary files after deployment

## Parameters

- `stack-name` (required): Name of the CloudFormation stack
- `region` (optional): AWS region for deployment (defaults to us-east-1)

## Monitoring Deployment

You can monitor the deployment progress in:
1. AWS CloudFormation console
2. AWS CLI using:
   ```bash
   aws cloudformation describe-stack-events --stack-name <stack-name>
   ```