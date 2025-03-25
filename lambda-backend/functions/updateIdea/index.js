const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.handler = async (event) => {
    try {
        const body = JSON.parse(event.body);
        const { ideaId } = event.pathParameters;
        const userId = event.requestContext.authorizer.claims.sub;
        const timestamp = new Date().toISOString();
        
        const result = await dynamodb.update({
            TableName: 'Ideas',
            Key: {
                ideaId,
                userId
            },
            UpdateExpression: 'SET title = :title, description = :description, updatedAt = :timestamp',
            ExpressionAttributeValues: {
                ':title': body.title,
                ':description': body.description,
                ':timestamp': timestamp
            },
            ReturnValues: 'ALL_NEW'
        }).promise();
        
        return {
            statusCode: 200,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(result.Attributes)
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
