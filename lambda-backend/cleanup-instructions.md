# Cleanup Instructions

This document explains how to clean up all deployed resources and local artifacts.

## Prerequisites

- AWS CLI installed and configured
- Proper AWS credentials set up
- Stack name used during deployment

## Usage

To clean up all resources, run:

```bash
# Make the script executable
chmod +x cleanup.sh

# Run the cleanup script with your stack name
./cleanup.sh <stack-name>
```

## What Gets Cleaned Up

### AWS Resources
- CloudFormation stack and all its resources:
  - DynamoDB tables
  - Cognito User Pool and Client
  - IAM Roles and Policies
  - Lambda functions

### Local Artifacts
- packaged.yaml
- samconfig.toml

## Script Behavior

The script will:
1. Verify AWS CLI is installed
2. Delete the CloudFormation stack
3. Wait for stack deletion to complete
4. Remove local deployment artifacts