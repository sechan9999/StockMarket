"""
Subscribe Lambda Function
Handles user email subscription with stock preferences
"""
import json
import boto3
import os
import re
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('SUBSCRIBERS_TABLE', 'stockpulse-subscribers'))

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def lambda_handler(event, context):
    """Handle subscription requests"""

    # CORS headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'OPTIONS,POST'
    }

    # Handle preflight
    if event.get('requestContext', {}).get('http', {}).get('method') == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}

    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        email = body.get('email', '').strip().lower()
        stocks = body.get('stocks', [])

        # Validate email
        if not email or not validate_email(email):
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Invalid email address'})
            }

        # Validate stocks (max 10)
        if not stocks or len(stocks) > 10:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Please select 1-10 stocks'})
            }

        # Clean stock symbols
        stocks = [s.upper().strip() for s in stocks if s.strip()]

        # Save to DynamoDB
        table.put_item(
            Item={
                'email': email,
                'stocks': stocks,
                'subscribed_at': datetime.utcnow().isoformat(),
                'active': True,
                'preferences': {
                    'frequency': 'daily',
                    'time': '08:00'
                }
            }
        )

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'message': 'Successfully subscribed!',
                'email': email,
                'stocks': stocks
            })
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Internal server error'})
        }
