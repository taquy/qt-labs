const AWS = require('aws-sdk');
const cognito = new AWS.CognitoIdentityServiceProvider();

exports.handler = async (event) => {
    try {
        const { email, password } = JSON.parse(event.body);
        
        const params = {
            AuthFlow: 'USER_PASSWORD_AUTH',
            ClientId: process.env.USER_POOL_CLIENT_ID,
            AuthParameters: {
                USERNAME: email,
                PASSWORD: password
            }
        };

        const result = await cognito.initiateAuth(params).promise();
        
        return {
            statusCode: 200,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            body: JSON.stringify({
                message: 'Login successful',
                accessToken: result.AuthenticationResult.AccessToken,
                idToken: result.AuthenticationResult.IdToken,
                refreshToken: result.AuthenticationResult.RefreshToken
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