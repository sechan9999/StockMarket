"""
Unsubscribe Lambda Function
Handles user email unsubscription
"""
import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('SUBSCRIBERS_TABLE', 'stockpulse-subscribers'))

def lambda_handler(event, context):
    """Handle unsubscription requests"""

    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
    }

    # Handle preflight
    if event.get('requestContext', {}).get('http', {}).get('method') == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}

    try:
        # Get email from query params or body
        email = None

        # Check query parameters (for GET requests from email links)
        query_params = event.get('queryStringParameters', {}) or {}
        email = query_params.get('email')

        # Check body (for POST requests)
        if not email and event.get('body'):
            body = json.loads(event.get('body', '{}'))
            email = body.get('email')

        if not email:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Email is required'})
            }

        email = email.strip().lower()

        # Update subscription status
        table.update_item(
            Key={'email': email},
            UpdateExpression='SET active = :active, unsubscribed_at = :time',
            ExpressionAttributeValues={
                ':active': False,
                ':time': __import__('datetime').datetime.utcnow().isoformat()
            }
        )

        # Return HTML for browser-based unsubscribe
        if query_params.get('email'):
            html_response = '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Unsubscribed - StockPulse AI</title>
                <style>
                    body { font-family: 'Inter', sans-serif; background: #0a0e17; color: white;
                           display: flex; justify-content: center; align-items: center;
                           height: 100vh; margin: 0; }
                    .container { text-align: center; padding: 2rem; }
                    h1 { color: #3b82f6; }
                    p { color: #94a3b8; }
                    a { color: #3b82f6; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Successfully Unsubscribed</h1>
                    <p>You will no longer receive StockPulse AI alerts.</p>
                    <p><a href="/">Return to StockPulse AI</a></p>
                </div>
            </body>
            </html>
            '''
            return {
                'statusCode': 200,
                'headers': {**headers, 'Content-Type': 'text/html'},
                'body': html_response
            }

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'message': 'Successfully unsubscribed'})
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Internal server error'})
        }
