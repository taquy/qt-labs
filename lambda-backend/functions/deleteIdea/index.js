const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.handler = async (event) => {
    try {
        const { ideaId } = event.pathParameters;
        const userId = event.requestContext.authorizer.claims.sub;
        
        await dynamodb.delete({
            TableName: 'Ideas',
            Key: {
                ideaId,
                userId
            }
        }).promise();
        
        return {
            statusCode: 200,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: 'Idea deleted successfully' })
        };
    } catch (error) {
        return {
            statusCode: 500,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ error: error.message })
        };
    }
};
