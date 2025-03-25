const AWS = require('aws-sdk');
const cognito = new AWS.CognitoIdentityServiceProvider();

exports.handler = async (event) => {
    try {
        const { email, password, name } = JSON.parse(event.body);
        
        const params = {
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

        const result = await cognito.signUp(params).promise();
        
        return {
            statusCode: 200,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            body: JSON.stringify({
                message: 'User registered successfully',
                userSub: result.UserSub,
                userConfirmed: result.UserConfirmed
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