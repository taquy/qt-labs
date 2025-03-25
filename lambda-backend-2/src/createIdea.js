const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();
const { v4: uuidv4 } = require('uuid');

exports.handler = async (event) => {
    try {
        const { title, description } = JSON.parse(event.body);
        const userId = event.requestContext.authorizer.claims.sub;
        
        const idea = {
            id: uuidv4(),
            userId,
            title,
            description,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
        };

        await dynamodb.put({
            TableName: process.env.IDEAS_TABLE,
            Item: idea
        }).promise();

        return {
            statusCode: 201,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            body: JSON.stringify({
                message: 'Idea created successfully',
                idea
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