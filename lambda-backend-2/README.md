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
- Node.js 18.x or later
- npm or yarn package manager

## Deployment

1. Install dependencies:
```bash
npm install
```

2. Deploy the CloudFormation stack:
```bash
aws cloudformation deploy \
  --template-file template.yaml \
  --stack-name idea-management-stack \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides EnvironmentName=dev
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

## Cleanup

To remove all resources:
```bash
aws cloudformation delete-stack --stack-name idea-management-stack
``` 