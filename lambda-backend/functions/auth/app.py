import json
import boto3
import os

def lambda_handler(event, context):
    cognito = boto3.client('cognito-idp')
    
    try:
        # Extract request data
        body = json.loads(event['body'])
        action = event['path'].split('/')[-1]  # 'login' or 'register'
        
        if action == 'register':
            response = cognito.sign_up(
                ClientId=os.environ['USER_POOL_CLIENT_ID'],
                Username=body['email'],
                Password=body['password'],
                UserAttributes=[
                    {'Name': 'email', 'Value': body['email']}
                ]
            )
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'User registered successfully',
                    'userSub': response['UserSub']
                })
            }
            
        elif action == 'login':
            response = cognito.initiate_auth(
                ClientId=os.environ['USER_POOL_CLIENT_ID'],
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': body['email'],
                    'PASSWORD': body['password']
                }
            )
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'token': response['AuthenticationResult']['IdToken']
                })
            }
            
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }