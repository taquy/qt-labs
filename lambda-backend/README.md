# Idea Management System

This project deploys a serverless idea management system using AWS CloudFormation. The system includes:
- Amazon Cognito for user authentication
- Amazon DynamoDB for storing ideas
- AWS Lambda functions for CRUD operations

## Prerequisites

1. AWS CLI installed and configured
2. Appropriate AWS permissions to create resources

## Deployment Instructions

1. Clone this repository:

```bash
git clone <repository-url>
cd idea-management-system

aws cloudformation create-stack \
  --stack-name idea-management-system \
  --template-body file://template.yaml \
  --capabilities CAPABILITY_IAM

aws cloudformation describe-stacks \
  --stack-name idea-management-system

aws cognito-idp sign-up \
  --client-id <UserPoolClientId> \
  --username <email> \
  --password <password>

aws cognito-idp admin-confirm-sign-up \
  --user-pool-id <UserPoolId> \
  --username <email>

aws cognito-idp initiate-auth \
  --client-id <UserPoolClientId> \
  --auth-flow USER_PASSWORD_AUTH \
  --auth-parameters USERNAME=<email>,PASSWORD=<password>
```

This implementation provides:
1. A secure authentication system using Cognito
2. A DynamoDB table with userId and ideaId as composite key
3. Four Lambda functions for CRUD operations
4. Proper IAM roles and permissions
5. Detailed deployment instructions

The system is designed to be secure and scalable, with each user only able to access their own ideas. The Lambda functions include error handling and proper response formatting.
