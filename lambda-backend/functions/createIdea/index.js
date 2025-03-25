const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();
const { v4: uuidv4 } = require('uuid');

exports.handler = async (event) => {
    try {
        const body = JSON.parse(event.body);
        const ideaId = uuidv4();
        const timestamp = new Date().toISOString();
        
        const item = {
            ideaId,
            userId: event.requestContext.authorizer.claims.sub,
            title: body.title,
            description: body.description,
            createdAt: timestamp,
            updatedAt: timestamp
        };
        
        await dynamodb.put({
            TableName: 'Ideas',
            Item: item
        }).promise();
        
        return {
            statusCode: 200,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: 'Idea created successfully',
                ideaId
            })
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
