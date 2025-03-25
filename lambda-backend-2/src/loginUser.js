const { CognitoIdentityProviderClient, InitiateAuthCommand } = require("@aws-sdk/client-cognito-identity-provider");

const cognitoClient = new CognitoIdentityProviderClient();

exports.handler = async (event) => {
    try {
        // Log the entire event object
        console.log('Received event:', JSON.stringify(event, null, 2));
        console.log('Event type:', typeof event);
        console.log('Event body type:', typeof event.body);
        
        // Parse event body
        let body;
        try {
            if (!event.body) {
                console.log('No body in event');
                return {
                    statusCode: 400,
                    headers: {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    body: JSON.stringify({
                        message: 'Request body is required'
                    })
                };
            }

            // Handle base64 encoded body
            const decodedBody = event.isBase64Encoded ? 
                Buffer.from(event.body, 'base64').toString('utf8') : 
                event.body;
            
            console.log('Decoded body:', decodedBody);
            
            // Try to parse the body
            body = typeof decodedBody === 'string' ? JSON.parse(decodedBody) : decodedBody;
            console.log('Parsed body:', JSON.stringify(body, null, 2));
        } catch (parseError) {
            console.error('Error parsing event body:', parseError);
            console.error('Raw body that caused error:', event.body);
            return {
                statusCode: 400,
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                body: JSON.stringify({
                    message: 'Invalid JSON in request body',
                    error: parseError.message
                })
            };
        }

        const { email, password } = body;

        if (!email || !password) {
            return {
                statusCode: 400,
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                body: JSON.stringify({
                    message: 'Email and password are required'
                })
            };
        }
        
        // Use USER_PASSWORD_AUTH flow
        const initiateAuthParams = {
            AuthFlow: 'USER_PASSWORD_AUTH',
            ClientId: process.env.USER_POOL_CLIENT_ID,
            AuthParameters: {
                USERNAME: email,
                PASSWORD: password
            }
        };

        console.log('Attempting login for user:', email);
        const initiateAuthCommand = new InitiateAuthCommand(initiateAuthParams);
        const authResult = await cognitoClient.send(initiateAuthCommand);
        console.log('Login successful for user:', email);
        
        return {
            statusCode: 200,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            body: JSON.stringify({
                message: 'Login successful',
                accessToken: authResult.AuthenticationResult.AccessToken,
                idToken: authResult.AuthenticationResult.IdToken,
                refreshToken: authResult.AuthenticationResult.RefreshToken
            })
        };
    } catch (error) {
        console.error('Login error:', error);
        
        // Handle specific Cognito errors
        let statusCode = 500;
        let message = 'Internal server error';
        
        if (error.name === 'NotAuthorizedException') {
            statusCode = 401;
            message = 'Invalid email or password';
        } else if (error.name === 'UserNotFoundException') {
            statusCode = 404;
            message = 'User not found';
        } else if (error.name === 'UserNotConfirmedException') {
            statusCode = 403;
            message = 'User is not confirmed';
        }

        return {
            statusCode,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            body: JSON.stringify({
                message,
                error: error.name || 'UnknownError'
            })
        };
    }
}; 