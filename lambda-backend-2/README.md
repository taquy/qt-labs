# Idea Management Application Backend

This is the backend implementation for an Idea Management application using AWS services. The application uses Lambda functions for serverless computing, DynamoDB for data storage, Cognito for user authentication, and API Gateway for REST API endpoints.

## Architecture

The application consists of the following AWS services:
- AWS Lambda for serverless functions
- Amazon DynamoDB for data storage
- Amazon Cognito for user authentication
- Amazon API Gateway for REST API endpoints
- Amazon S3 for CloudFormation state storage

## Prerequisites

- AWS CLI installed and configured
- AWS SAM CLI installed (for packaging and deploying Lambda functions)
- Node.js 18.x or later
- npm or yarn package manager
- AWS credentials configured with appropriate permissions

## Deployment

### Using Deployment Script

The project includes a deployment script (`deploy.sh`) that automates the deployment process:

1. Make the script executable:
```bash
chmod +x deploy.sh
```

2. Run the deployment script:
```bash
./deploy.sh
```

The script will:
- Check for required prerequisites (AWS CLI, npm, SAM CLI)
- Create an S3 bucket for packaging (if it doesn't exist)
- Install project dependencies
- Package the Lambda functions
- Deploy the CloudFormation stack
- Display stack outputs upon successful deployment

### Manual Deployment

If you prefer to deploy manually:

1. Install dependencies:
```bash
npm install
```

2. Package the application:
```bash
sam package \
  --template-file template.yaml \
  --output-template-file packaged.yaml \
  --s3-bucket your-package-bucket \
  --region ap-southeast-1
```

3. Deploy the CloudFormation stack:
```bash
sam deploy \
  --template-file packaged.yaml \
  --stack-name idea-management-stack \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides EnvironmentName=dev \
  --region ap-southeast-1
```

## Cleanup

### Using Cleanup Script

The project includes a cleanup script (`cleanup.sh`) that safely removes all resources:

1. Make the script executable:
```bash
chmod +x cleanup.sh
```

2. Run the cleanup script:
```bash
./cleanup.sh
```

The script will:
- Check for required prerequisites (AWS CLI)
- Verify stack existence
- Ask for confirmation before deletion
- Delete the CloudFormation stack
- Clean up all related S3 buckets (including the packaging bucket)
- Remove local files (node_modules, package-lock.json, packaged.yaml)

Note: The cleanup script will remove all S3 buckets that start with 'idea-management' prefix. Make sure you don't have any other important buckets with this prefix.

### Manual Cleanup

To remove all resources manually:

1. Delete the CloudFormation stack:
```bash
aws cloudformation delete-stack --stack-name idea-management-stack --region ap-southeast-1
```

2. Empty and delete the packaging bucket:
```bash
aws s3api delete-objects \
  --bucket idea-management-package-dev \
  --delete "$(aws s3api list-object-versions \
    --bucket idea-management-package-dev \
    --output json \
    --query '{Objects: [].{Key:Key,VersionId:VersionId}}')" \
  --region ap-southeast-1

aws s3api delete-bucket --bucket idea-management-package-dev --region ap-southeast-1
```

## API Endpoints

### Authentication
- POST /auth/register - Register a new user
- POST /auth/login - Login user

### Ideas
- POST /ideas - Create a new idea
- GET /ideas/{id} - Get an idea by ID
- PUT /ideas/{id} - Update an idea
- DELETE /ideas/{id} - Delete an idea

## Authentication

The application uses Amazon Cognito for user authentication. All API endpoints except registration and login require a valid JWT token in the Authorization header.

### Register User
```bash
curl -X POST https://your-api-endpoint/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "name": "John Doe"
  }'
```

### Login
```bash
curl -X POST https://your-api-endpoint/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### Create Idea
```bash
curl -X POST https://your-api-endpoint/ideas \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "title": "My Idea",
    "description": "Description of my idea"
  }'
```

## Security

- All API endpoints are protected with Cognito authentication
- DynamoDB access is restricted to specific Lambda functions
- S3 bucket for CloudFormation state is private
- CORS is enabled for API endpoints

## Error Handling

The application includes comprehensive error handling for:
- Authentication failures
- Invalid input data
- Database errors
- API Gateway errors

## Monitoring and Logging

- CloudWatch Logs for Lambda functions
- CloudWatch Metrics for API Gateway
- DynamoDB metrics
- Cognito user pool metrics

## Configuration

The deployment and cleanup scripts use the following default values:
- Stack Name: `idea-management-stack`
- Environment: `dev`
- Region: `ap-southeast-1` (Singapore)

You can modify these values in the respective scripts if needed:
- `deploy.sh`: Edit the variables at the top of the file
- `cleanup.sh`: Edit the variables at the top of the file

Note: Make sure your AWS CLI is configured to use the correct region. You can set it using:
```bash
aws configure set region ap-southeast-1
``` 