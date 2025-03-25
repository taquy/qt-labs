const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.handler = async (event) => {
    try {
        const { id } = event.pathParameters;
        const { title, description } = JSON.parse(event.body);
        const userId = event.requestContext.authorizer.claims.sub;

        const updateExpression = [];
        const expressionAttributeNames = {};
        const expressionAttributeValues = {};

        if (title) {
            updateExpression.push('#title = :title');
            expressionAttributeNames['#title'] = 'title';
            expressionAttributeValues[':title'] = title;
        }

        if (description) {
            updateExpression.push('#description = :description');
            expressionAttributeNames['#description'] = 'description';
            expressionAttributeValues[':description'] = description;
        }

        updateExpression.push('#updatedAt = :updatedAt');
        expressionAttributeNames['#updatedAt'] = 'updatedAt';
        expressionAttributeValues[':updatedAt'] = new Date().toISOString();

        const result = await dynamodb.update({
            TableName: process.env.IDEAS_TABLE,
            Key: {
                id,
                userId
            },
            UpdateExpression: `SET ${updateExpression.join(', ')}`,
            ExpressionAttributeNames: expressionAttributeNames,
            ExpressionAttributeValues: expressionAttributeValues,
            ReturnValues: 'ALL_NEW'
        }).promise();

        return {
            statusCode: 200,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            body: JSON.stringify({
                message: 'Idea updated successfully',
                idea: result.Attributes
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