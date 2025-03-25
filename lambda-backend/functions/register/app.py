import json
import boto3
import os

def lambda_handler(event, context):
    try:
        # Get environment variables
        user_pool_id = os.environ['USER_POOL_ID']
        client_id = os.environ['CLIENT_ID']
        
        # Parse request body
        body = json.loads(event['body'])
        email = body['email']
        password = body['password']
        
        # Create Cognito client
        client = boto3.client('cognito-idp')
        
        # Sign up the user
        response = client.sign_up(
            ClientId=client_id,
            Username=email,
            Password=password,
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': email
                }
            ]
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'User registration successful',
                'userSub': response['UserSub']
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }