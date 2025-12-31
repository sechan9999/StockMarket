"""
Analyze Lambda Function
Real-time stock analysis using Alpha Vantage, NewsAPI, and Amazon Bedrock Claude
"""
import json
import boto3
import os
import urllib.request
from datetime import datetime, timedelta
from decimal import Decimal

# Clients
bedrock = boto3.client('bedrock-runtime', region_name=os.environ.get('AWS_REGION', 'us-east-2'))

# API Keys (from environment variables)
ALPHA_VANTAGE_KEY = os.environ.get('ALPHA_VANTAGE_KEY', 'demo')
NEWS_API_KEY = os.environ.get('NEWS_API_KEY', '')

def fetch_stock_data(symbol):
    """Fetch real-time stock data from Alpha Vantage"""
    try:
        # Global Quote endpoint for current price
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_KEY}"

        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())

        quote = data.get('Global Quote', {})

        if not quote:
            return None

        return {
            'symbol': symbol,
            'price': float(quote.get('05. price', 0)),
            'change': float(quote.get('09. change', 0)),
            'change_percent': quote.get('10. change percent', '0%').replace('%', ''),
            'volume': int(quote.get('06. volume', 0)),
            'previous_close': float(quote.get('08. previous close', 0)),
            'open': float(quote.get('02. open', 0)),
            'high': float(quote.get('03. high', 0)),
            'low': float(quote.get('04. low', 0))
        }
    except Exception as e:
        print(f"Error fetching stock data for {symbol}: {e}")
        return None

def fetch_technical_indicators(symbol):
    """Fetch RSI and other technical indicators"""
    indicators = {}

    try:
        # RSI
        url = f"https://www.alphavantage.co/query?function=RSI&symbol={symbol}&interval=daily&time_period=14&series_type=close&apikey={ALPHA_VANTAGE_KEY}"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())

        rsi_data = data.get('Technical Analysis: RSI', {})
        if rsi_data:
            latest_date = list(rsi_data.keys())[0]
            indicators['rsi'] = float(rsi_data[latest_date]['RSI'])
    except Exception as e:
        print(f"Error fetching RSI: {e}")
        indicators['rsi'] = None

    try:
        # MACD
        url = f"https://www.alphavantage.co/query?function=MACD&symbol={symbol}&interval=daily&series_type=close&apikey={ALPHA_VANTAGE_KEY}"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())

        macd_data = data.get('Technical Analysis: MACD', {})
        if macd_data:
            latest_date = list(macd_data.keys())[0]
            indicators['macd'] = float(macd_data[latest_date]['MACD'])
            indicators['macd_signal'] = float(macd_data[latest_date]['MACD_Signal'])
            indicators['macd_hist'] = float(macd_data[latest_date]['MACD_Hist'])
    except Exception as e:
        print(f"Error fetching MACD: {e}")
        indicators['macd'] = None

    return indicators

def fetch_news(symbol):
    """Fetch recent news articles about the stock"""
    if not NEWS_API_KEY:
        return []

    try:
        # Get company name mapping
        company_names = {
            'AAPL': 'Apple',
            'GOOGL': 'Google OR Alphabet',
            'MSFT': 'Microsoft',
            'AMZN': 'Amazon',
            'TSLA': 'Tesla',
            'NVDA': 'NVIDIA',
            'META': 'Meta OR Facebook'
        }

        query = company_names.get(symbol, symbol)
        from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

        url = f"https://newsapi.org/v2/everything?q={query}&from={from_date}&sortBy=relevancy&pageSize=5&apiKey={NEWS_API_KEY}"

        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())

        articles = data.get('articles', [])
        return [
            {
                'title': a.get('title', ''),
                'description': a.get('description', ''),
                'source': a.get('source', {}).get('name', ''),
                'url': a.get('url', ''),
                'publishedAt': a.get('publishedAt', '')
            }
            for a in articles[:5]
        ]
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

def analyze_with_bedrock(stock_data, indicators, news):
    """Use Amazon Bedrock Claude to analyze stock data"""

    # Build prompt
    prompt = f"""You are a professional stock analyst. Analyze the following stock data and provide insights.

## Stock Data for {stock_data['symbol']}
- Current Price: ${stock_data['price']:.2f}
- Change: ${stock_data['change']:.2f} ({stock_data['change_percent']}%)
- Volume: {stock_data['volume']:,}
- Day Range: ${stock_data['low']:.2f} - ${stock_data['high']:.2f}

## Technical Indicators
- RSI (14-day): {indicators.get('rsi', 'N/A')}
- MACD: {indicators.get('macd', 'N/A')}
- MACD Signal: {indicators.get('macd_signal', 'N/A')}
- MACD Histogram: {indicators.get('macd_hist', 'N/A')}

## Recent News Headlines
{chr(10).join([f"- {n['title']} ({n['source']})" for n in news]) if news else "No recent news available"}

Based on this data, provide:
1. **Sentiment Analysis**: Classify as Bullish, Bearish, or Neutral with confidence percentage
2. **Technical Analysis**: Interpret RSI and MACD signals (BUY/SELL/HOLD)
3. **7-Day Price Prediction**: Predict direction and approximate percentage change
4. **Final Recommendation**: STRONG_BUY, BUY, HOLD, SELL, or STRONG_SELL with reasoning
5. **Risk Level**: Low, Medium, or High

Format your response as JSON with these exact keys:
{{
    "sentiment": {{"label": "Bullish/Bearish/Neutral", "confidence": 75}},
    "technical": {{"rsi_signal": "BUY/SELL/HOLD", "macd_signal": "BUY/SELL/HOLD", "overall": "BUY/SELL/HOLD", "score": 72}},
    "prediction": {{"direction": "up/down/neutral", "percent": 5.2, "confidence": 70}},
    "recommendation": {{"rating": "STRONG_BUY/BUY/HOLD/SELL/STRONG_SELL", "score": 8.5, "reasoning": "Brief explanation"}},
    "risk": "Low/Medium/High",
    "summary": "2-3 sentence executive summary"
}}
"""

    try:
        # Call Bedrock Claude
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            contentType='application/json',
            accept='application/json',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 1024,
                'messages': [
                    {'role': 'user', 'content': prompt}
                ]
            })
        )

        result = json.loads(response['body'].read())
        content = result['content'][0]['text']

        # Extract JSON from response
        import re
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            return json.loads(json_match.group())

        return None

    except Exception as e:
        print(f"Error calling Bedrock: {e}")
        return None

def generate_fallback_analysis(stock_data, indicators):
    """Generate analysis without Bedrock (fallback)"""
    rsi = indicators.get('rsi', 50)
    macd = indicators.get('macd', 0)
    change = float(stock_data.get('change_percent', 0))

    # Simple rule-based analysis
    sentiment = 'Neutral'
    sentiment_conf = 60
    if change > 2:
        sentiment = 'Bullish'
        sentiment_conf = 75
    elif change < -2:
        sentiment = 'Bearish'
        sentiment_conf = 75

    rsi_signal = 'HOLD'
    if rsi and rsi < 30:
        rsi_signal = 'BUY'
    elif rsi and rsi > 70:
        rsi_signal = 'SELL'

    macd_signal = 'HOLD'
    if macd and macd > 0:
        macd_signal = 'BUY'
    elif macd and macd < 0:
        macd_signal = 'SELL'

    # Calculate overall
    signals = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
    signals[rsi_signal] += 1
    signals[macd_signal] += 1
    if change > 0:
        signals['BUY'] += 1
    elif change < 0:
        signals['SELL'] += 1
    else:
        signals['HOLD'] += 1

    overall = max(signals, key=signals.get)

    recommendation = 'HOLD'
    if signals['BUY'] >= 2:
        recommendation = 'BUY' if signals['BUY'] == 2 else 'STRONG_BUY'
    elif signals['SELL'] >= 2:
        recommendation = 'SELL' if signals['SELL'] == 2 else 'STRONG_SELL'

    return {
        'sentiment': {'label': sentiment, 'confidence': sentiment_conf},
        'technical': {
            'rsi_signal': rsi_signal,
            'macd_signal': macd_signal,
            'overall': overall,
            'score': 50 + (signals['BUY'] - signals['SELL']) * 15
        },
        'prediction': {
            'direction': 'up' if change > 0 else 'down' if change < 0 else 'neutral',
            'percent': abs(change) * 1.5,
            'confidence': 55
        },
        'recommendation': {
            'rating': recommendation,
            'score': 5 + (signals['BUY'] - signals['SELL']) * 1.5,
            'reasoning': f"Based on RSI ({rsi:.1f if rsi else 'N/A'}) and MACD signals"
        },
        'risk': 'Medium',
        'summary': f"{stock_data['symbol']} shows {sentiment.lower()} sentiment with {overall.lower()} technical signals."
    }

def lambda_handler(event, context):
    """Main handler for stock analysis requests"""

    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
    }

    if event.get('requestContext', {}).get('http', {}).get('method') == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}

    try:
        # Get symbol from query params or body
        symbol = None

        query_params = event.get('queryStringParameters', {}) or {}
        symbol = query_params.get('symbol')

        if not symbol and event.get('body'):
            body = json.loads(event.get('body', '{}'))
            symbol = body.get('symbol')

        if not symbol:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Stock symbol is required'})
            }

        symbol = symbol.upper().strip()

        # Fetch all data
        stock_data = fetch_stock_data(symbol)

        if not stock_data:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': f'Could not fetch data for {symbol}'})
            }

        indicators = fetch_technical_indicators(symbol)
        news = fetch_news(symbol)

        # Analyze with Bedrock or fallback
        analysis = analyze_with_bedrock(stock_data, indicators, news)

        if not analysis:
            analysis = generate_fallback_analysis(stock_data, indicators)

        # Build response
        response_data = {
            'symbol': symbol,
            'timestamp': datetime.utcnow().isoformat(),
            'stock_data': stock_data,
            'indicators': indicators,
            'news': news,
            'analysis': analysis
        }

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(response_data, default=str)
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Internal server error'})
        }
