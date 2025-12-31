"""
Daily Digest Lambda Function
Triggered by EventBridge to send daily stock analysis emails via SES
"""
import json
import boto3
import os
from datetime import datetime
from analyze import fetch_stock_data, fetch_technical_indicators, fetch_news, analyze_with_bedrock, generate_fallback_analysis

# AWS Clients
dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses', region_name=os.environ.get('AWS_REGION', 'us-east-2'))

SUBSCRIBERS_TABLE = os.environ.get('SUBSCRIBERS_TABLE', 'stockpulse-subscribers')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'noreply@stockpulse.ai')
API_GATEWAY_URL = os.environ.get('API_GATEWAY_URL', '')

def get_active_subscribers():
    """Fetch all active subscribers from DynamoDB"""
    table = dynamodb.Table(SUBSCRIBERS_TABLE)

    try:
        response = table.scan(
            FilterExpression='active = :active',
            ExpressionAttributeValues={':active': True}
        )
        return response.get('Items', [])
    except Exception as e:
        print(f"Error fetching subscribers: {e}")
        return []

def generate_email_html(email, stocks_analysis):
    """Generate beautiful HTML email with stock analysis"""

    # Unsubscribe URL
    unsubscribe_url = f"{API_GATEWAY_URL}/unsubscribe?email={email}"

    # Build stock cards HTML
    stock_cards = ""
    for analysis in stocks_analysis:
        symbol = analysis['symbol']
        data = analysis['stock_data']
        ai = analysis['analysis']

        change_color = '#10b981' if data['change'] >= 0 else '#ef4444'
        change_sign = '+' if data['change'] >= 0 else ''

        rating_colors = {
            'STRONG_BUY': '#059669',
            'BUY': '#10b981',
            'HOLD': '#f59e0b',
            'SELL': '#ef4444',
            'STRONG_SELL': '#dc2626'
        }
        rating = ai['recommendation']['rating']
        rating_color = rating_colors.get(rating, '#64748b')

        stock_cards += f'''
        <div style="background: #1a2235; border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.1);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <div>
                    <h2 style="margin: 0; color: #fff; font-size: 24px;">{symbol}</h2>
                    <p style="margin: 5px 0 0; color: #94a3b8; font-size: 14px;">Updated: {datetime.now().strftime("%B %d, %Y")}</p>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 28px; font-weight: bold; color: #fff;">${data['price']:.2f}</div>
                    <div style="color: {change_color}; font-size: 16px;">{change_sign}{data['change']:.2f} ({change_sign}{data['change_percent']}%)</div>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 15px;">
                <div style="background: #111827; padding: 12px; border-radius: 8px; text-align: center;">
                    <div style="color: #94a3b8; font-size: 12px;">Sentiment</div>
                    <div style="color: #10b981; font-size: 18px; font-weight: bold;">{ai['sentiment']['label']}</div>
                    <div style="color: #64748b; font-size: 11px;">{ai['sentiment']['confidence']}% confidence</div>
                </div>
                <div style="background: #111827; padding: 12px; border-radius: 8px; text-align: center;">
                    <div style="color: #94a3b8; font-size: 12px;">Technical</div>
                    <div style="color: #3b82f6; font-size: 18px; font-weight: bold;">{ai['technical']['overall']}</div>
                    <div style="color: #64748b; font-size: 11px;">Score: {ai['technical']['score']}</div>
                </div>
                <div style="background: #111827; padding: 12px; border-radius: 8px; text-align: center;">
                    <div style="color: #94a3b8; font-size: 12px;">7-Day Forecast</div>
                    <div style="color: {'#10b981' if ai['prediction']['direction'] == 'up' else '#ef4444'}; font-size: 18px; font-weight: bold;">
                        {'↑' if ai['prediction']['direction'] == 'up' else '↓'} {ai['prediction']['percent']:.1f}%
                    </div>
                    <div style="color: #64748b; font-size: 11px;">{ai['prediction']['confidence']}% confidence</div>
                </div>
                <div style="background: #111827; padding: 12px; border-radius: 8px; text-align: center;">
                    <div style="color: #94a3b8; font-size: 12px;">Rating</div>
                    <div style="color: {rating_color}; font-size: 16px; font-weight: bold;">{rating.replace('_', ' ')}</div>
                    <div style="color: #64748b; font-size: 11px;">Score: {ai['recommendation']['score']:.1f}/10</div>
                </div>
            </div>

            <div style="background: #111827; padding: 15px; border-radius: 8px;">
                <p style="margin: 0; color: #e2e8f0; font-size: 14px; line-height: 1.6;">
                    <strong style="color: #3b82f6;">AI Summary:</strong> {ai['summary']}
                </p>
            </div>
        </div>
        '''

    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; background: #0a0e17; font-family: 'Segoe UI', Arial, sans-serif;">
        <div style="max-width: 700px; margin: 0 auto; padding: 20px;">
            <!-- Header -->
            <div style="text-align: center; padding: 30px 0;">
                <h1 style="margin: 0; color: #3b82f6; font-size: 32px;">
                    📈 StockPulse<span style="background: linear-gradient(135deg, #3b82f6, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">AI</span>
                </h1>
                <p style="color: #94a3b8; margin: 10px 0 0;">Your Daily Stock Intelligence Report</p>
                <p style="color: #64748b; font-size: 12px;">{datetime.now().strftime("%A, %B %d, %Y")}</p>
            </div>

            <!-- Stock Analysis Cards -->
            {stock_cards}

            <!-- Footer -->
            <div style="text-align: center; padding: 30px 0; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 30px;">
                <p style="color: #64748b; font-size: 12px; margin-bottom: 15px;">
                    ⚠️ This is for educational purposes only. Not financial advice.
                </p>
                <p style="color: #64748b; font-size: 12px;">
                    <a href="{unsubscribe_url}" style="color: #3b82f6;">Unsubscribe</a>
                </p>
                <p style="color: #4b5563; font-size: 11px; margin-top: 15px;">
                    © 2025 StockPulse AI. Powered by Amazon Bedrock.
                </p>
            </div>
        </div>
    </body>
    </html>
    '''

    return html

def send_email(to_email, subject, html_body):
    """Send email via Amazon SES"""
    try:
        response = ses.send_email(
            Source=SENDER_EMAIL,
            Destination={'ToAddresses': [to_email]},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {
                    'Html': {'Data': html_body, 'Charset': 'UTF-8'}
                }
            }
        )
        print(f"Email sent to {to_email}: {response['MessageId']}")
        return True
    except Exception as e:
        print(f"Error sending email to {to_email}: {e}")
        return False

def lambda_handler(event, context):
    """Main handler - triggered by EventBridge daily"""

    print(f"Starting daily digest at {datetime.utcnow().isoformat()}")

    # Get all active subscribers
    subscribers = get_active_subscribers()
    print(f"Found {len(subscribers)} active subscribers")

    emails_sent = 0
    errors = 0

    for subscriber in subscribers:
        email = subscriber.get('email')
        stocks = subscriber.get('stocks', [])

        if not email or not stocks:
            continue

        print(f"Processing {email} with stocks: {stocks}")

        # Analyze each stock
        stocks_analysis = []
        for symbol in stocks[:5]:  # Limit to 5 stocks per user
            try:
                stock_data = fetch_stock_data(symbol)
                if not stock_data:
                    continue

                indicators = fetch_technical_indicators(symbol)
                news = fetch_news(symbol)

                # Try Bedrock, fallback to rule-based
                analysis = analyze_with_bedrock(stock_data, indicators, news)
                if not analysis:
                    analysis = generate_fallback_analysis(stock_data, indicators)

                stocks_analysis.append({
                    'symbol': symbol,
                    'stock_data': stock_data,
                    'analysis': analysis
                })
            except Exception as e:
                print(f"Error analyzing {symbol}: {e}")
                continue

        if not stocks_analysis:
            print(f"No analysis available for {email}")
            continue

        # Generate and send email
        html = generate_email_html(email, stocks_analysis)
        subject = f"📈 StockPulse AI Daily Report - {datetime.now().strftime('%B %d, %Y')}"

        if send_email(email, subject, html):
            emails_sent += 1
        else:
            errors += 1

    print(f"Daily digest complete. Sent: {emails_sent}, Errors: {errors}")

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Daily digest complete',
            'emails_sent': emails_sent,
            'errors': errors
        })
    }
