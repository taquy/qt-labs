const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.handler = async (event) => {
    try {
        const { id } = event.pathParameters;
        const userId = event.requestContext.authorizer.claims.sub;

        await dynamodb.delete({
            TableName: process.env.IDEAS_TABLE,
            Key: {
                id,
                userId
            }
        }).promise();

        return {
            statusCode: 200,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            body: JSON.stringify({
                message: 'Idea deleted successfully'
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