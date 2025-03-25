const AWS = require('aws-sdk');
const cognito = new AWS.CognitoIdentityServiceProvider();

exports.handler = async (event) => {
    try {
        const { email, password } = JSON.parse(event.body);
        
        // Step 1: Initiate Auth
        const initiateAuthParams = {
            AuthFlow: 'USER_SRP_AUTH',
            ClientId: process.env.USER_POOL_CLIENT_ID,
            AuthParameters: {
                USERNAME: email,
                SRP_A: password // In a real implementation, this would be the SRP A value
            }
        };

        const initiateAuthResult = await cognito.initiateAuth(initiateAuthParams).promise();
        
        // Step 2: Respond to Auth Challenge
        const respondToAuthChallengeParams = {
            ChallengeName: initiateAuthResult.ChallengeName,
            ClientId: process.env.USER_POOL_CLIENT_ID,
            ChallengeResponses: {
                USERNAME: email,
                SRP_B: password // In a real implementation, this would be the SRP B value
            },
            Session: initiateAuthResult.Session
        };

        const authResult = await cognito.respondToAuthChallenge(respondToAuthChallengeParams).promise();
        
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