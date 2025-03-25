const AWS = require('aws-sdk');
const cognito = new AWS.CognitoIdentityServiceProvider();

exports.handler = async (event) => {
    try {
        const { email, password, name } = JSON.parse(event.body);
        
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

        const signUpResult = await cognito.signUp(signUpParams).promise();
        
        // Step 2: Auto-confirm the user
        const confirmParams = {
            ClientId: process.env.USER_POOL_CLIENT_ID,
            Username: email,
            ConfirmationCode: '123456' // Default code for auto-confirmation
        };

        try {
            await cognito.confirmSignUp(confirmParams).promise();
            
            // Step 3: Set user password to permanent
            const setPasswordParams = {
                Password: password,
                Permanent: true,
                Username: email,
                UserPoolId: process.env.USER_POOL_ID
            };
            
            await cognito.adminSetUserPassword(setPasswordParams).promise();
        } catch (confirmError) {
            console.log('Auto-confirmation failed, user might need manual confirmation:', confirmError);
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
        console.error('Error:', error);
        return {
            statusCode: error.statusCode || 500,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            body: JSON.stringify({
                message: error.message || 'Internal server error'
            })
        };
    }
}; 