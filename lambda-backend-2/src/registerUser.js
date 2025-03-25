const { CognitoIdentityProviderClient, SignUpCommand, ConfirmSignUpCommand, AdminConfirmSignUpCommand, AdminSetUserPasswordCommand } = require("@aws-sdk/client-cognito-identity-provider");

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

        const { email, password, name } = body;

        if (!email || !password || !name) {
            return {
                statusCode: 400,
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                body: JSON.stringify({
                    message: 'Email, password, and name are required'
                })
            };
        }
        
        // Step 1: Sign up the user
        const signUpParams = {
            ClientId: process.env.USER_POOL_CLIENT_ID,
            Username: email,
            Password: password,
            UserAttributes: [
                {
                    Name: 'email',
                    Value: email
                },
                {
                    Name: 'name',
                    Value: name
                }
            ]
        };

        console.log('Attempting to sign up user:', email);
        const signUpCommand = new SignUpCommand(signUpParams);
        const signUpResult = await cognitoClient.send(signUpCommand);
        console.log('Sign up successful:', signUpResult);
        
        // Step 2: Auto-confirm the user
        const confirmParams = {
            ClientId: process.env.USER_POOL_CLIENT_ID,
            Username: email,
            ConfirmationCode: '123456' // Default code for auto-confirmation
        };

        try {
            console.log('Attempting to confirm user:', email);
            const confirmCommand = new ConfirmSignUpCommand(confirmParams);
            await cognitoClient.send(confirmCommand);
            console.log('User confirmed successfully');
            
            // Step 3: Set user password to permanent
            const setPasswordParams = {
                Password: password,
                Permanent: true,
                Username: email,
                UserPoolId: process.env.USER_POOL_ID
            };
            
            console.log('Attempting to set permanent password for user:', email);
            const setPasswordCommand = new AdminSetUserPasswordCommand(setPasswordParams);
            await cognitoClient.send(setPasswordCommand);
            console.log('Password set successfully');
        } catch (confirmError) {
            console.error('Error during confirmation or password setting:', confirmError);
            // If confirmation fails, try admin confirm
            try {
                console.log('Attempting admin confirmation for user:', email);
                const adminConfirmParams = {
                    UserPoolId: process.env.USER_POOL_ID,
                    Username: email
                };
                const adminConfirmCommand = new AdminConfirmSignUpCommand(adminConfirmParams);
                await cognitoClient.send(adminConfirmCommand);
                console.log('Admin confirmation successful');
            } catch (adminConfirmError) {
                console.error('Admin confirmation failed:', adminConfirmError);
                throw adminConfirmError;
            }
        }
        
        return {
            statusCode: 200,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            body: JSON.stringify({
                message: 'User registered successfully',
                userSub: signUpResult.UserSub,
                userConfirmed: signUpResult.UserConfirmed
            })
        };
    } catch (error) {
        console.error('Registration error:', error);
        
        // Handle specific Cognito errors
        let statusCode = 500;
        let message = 'Internal server error';
        
        if (error.name === 'UsernameExistsException') {
            statusCode = 409;
            message = 'User already exists';
        } else if (error.name === 'InvalidPasswordException') {
            statusCode = 400;
            message = 'Password does not meet requirements';
        } else if (error.name === 'InvalidParameterException') {
            statusCode = 400;
            message = 'Invalid parameters provided';
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