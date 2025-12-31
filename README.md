# StockPulse AI 📈

> **Real-time AI-powered stock analysis platform with daily email alerts**

A fully serverless stock intelligence platform built on AWS, featuring real-time market data, AI-powered analysis using Amazon Bedrock Claude, and automated daily email reports.

![Architecture](https://img.shields.io/badge/AWS-Serverless-orange)
![AI](https://img.shields.io/badge/AI-Bedrock%20Claude-blue)
![Status](https://img.shields.io/badge/Status-Production%20Ready-green)

## 🌟 Features

| Feature | Description |
|---------|-------------|
| **Real-time Stock Data** | Live prices from Alpha Vantage API |
| **AI Sentiment Analysis** | FinBERT-style analysis via Claude |
| **Technical Indicators** | RSI, MACD, Bollinger Bands |
| **7-Day Predictions** | AI-powered price forecasts |
| **Daily Email Alerts** | Automated reports at 8 AM EST |
| **Subscription System** | User-managed stock watchlists |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CloudFront + S3                          │
│                    (React/HTML Frontend)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       API Gateway (HTTP)                        │
│              /subscribe  /unsubscribe  /analyze                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Subscribe  │    │  Unsubscribe │    │   Analyze    │
│    Lambda    │    │    Lambda    │    │    Lambda    │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                         DynamoDB                                │
│                    (User Subscriptions)                         │
└─────────────────────────────────────────────────────────────────┘
                             │
                             │ EventBridge (8 AM EST)
                             ▼
                    ┌──────────────┐
                    │ Daily Digest │
                    │    Lambda    │
                    └──────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│Alpha Vantage │  │   NewsAPI    │  │   Bedrock    │
│  (Prices)    │  │   (News)     │  │   Claude     │
└──────────────┘  └──────────────┘  └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  Amazon SES  │
                    │   (Email)    │
                    └──────────────┘
```

## 🚀 Quick Deploy (AWS CloudShell)

### Prerequisites
1. AWS Account with admin access
2. [Alpha Vantage API Key](https://www.alphavantage.co/support/#api-key) (Free)
3. [NewsAPI Key](https://newsapi.org/) (Free, optional)
4. Verified email in Amazon SES

### Step 1: Clone Repository
```bash
git clone https://github.com/sechan9999/StockMarket.git
cd StockMarket
```

### Step 2: Set Environment Variables
```bash
export AWS_REGION="us-east-2"
export ALPHA_VANTAGE_KEY="your_alpha_vantage_key"
export NEWS_API_KEY="your_newsapi_key"
export SENDER_EMAIL="your-verified-email@example.com"
```

### Step 3: Deploy Infrastructure
```bash
# Deploy CloudFormation stack
aws cloudformation deploy \
    --template-file infrastructure/template.yaml \
    --stack-name stockpulse-ai \
    --region us-east-2 \
    --capabilities CAPABILITY_NAMED_IAM \
    --parameter-overrides \
        AlphaVantageApiKey=$ALPHA_VANTAGE_KEY \
        NewsApiKey=$NEWS_API_KEY \
        SenderEmail=$SENDER_EMAIL
```

### Step 4: Get API URL
```bash
API_URL=$(aws cloudformation describe-stacks \
    --stack-name stockpulse-ai \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
    --output text)
echo "API URL: $API_URL"
```

### Step 5: Deploy Lambda Code
```bash
cd backend/lambda

# Package and deploy each function
for func in subscribe unsubscribe analyze daily_digest; do
    zip ${func}.zip ${func}.py
    aws lambda update-function-code \
        --function-name stockpulse-${func//_/-}-prod \
        --zip-file fileb://${func}.zip
done

cd ../..
```

### Step 6: Update Frontend & Deploy
```bash
# Update API URL in frontend
sed -i "s|YOUR_API_GATEWAY_URL|${API_URL}|g" frontend/index.html

# Get bucket name
BUCKET=$(aws cloudformation describe-stacks \
    --stack-name stockpulse-ai \
    --query 'Stacks[0].Outputs[?OutputKey==`FrontendBucketName`].OutputValue' \
    --output text)

# Upload frontend
aws s3 sync frontend/ s3://$BUCKET/ --delete
```

### Step 7: Enable Bedrock Claude
1. Go to AWS Console → Amazon Bedrock
2. Navigate to Model Access
3. Enable **Claude 3 Sonnet** model

### Step 8: Verify SES Email
```bash
aws ses verify-email-identity --email-address your-email@example.com
```

## 📁 Project Structure

```
StockMarket/
├── backend/
│   └── lambda/
│       ├── subscribe.py      # Email subscription handler
│       ├── unsubscribe.py    # Unsubscription handler
│       ├── analyze.py        # Real-time stock analysis
│       └── daily_digest.py   # Daily email reports
├── frontend/
│   └── index.html            # Full-featured web app
├── infrastructure/
│   └── template.yaml         # CloudFormation template
├── deploy.sh                 # Automated deployment script
└── README.md
```

## 🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/subscribe` | Subscribe to daily alerts |
| GET | `/unsubscribe?email=` | Unsubscribe from alerts |
| GET | `/analyze?symbol=AAPL` | Get real-time analysis |
| POST | `/analyze` | Analyze with custom params |

### Example: Analyze Stock
```bash
curl "https://your-api.execute-api.us-east-2.amazonaws.com/analyze?symbol=AAPL"
```

Response:
```json
{
  "symbol": "AAPL",
  "stock_data": {
    "price": 198.56,
    "change": 2.34,
    "change_percent": "1.19"
  },
  "analysis": {
    "sentiment": {"label": "Bullish", "confidence": 78},
    "technical": {"overall": "BUY", "score": 72},
    "prediction": {"direction": "up", "percent": 5.2},
    "recommendation": {"rating": "STRONG_BUY", "score": 8.5}
  }
}
```

## 💰 Cost Estimation

| Service | Monthly Cost (Est.) |
|---------|---------------------|
| Lambda | ~$1-5 (free tier eligible) |
| API Gateway | ~$1-3 |
| DynamoDB | ~$1 (on-demand) |
| S3 + CloudFront | ~$1 |
| SES | $0.10/1000 emails |
| Bedrock Claude | ~$0.003/1K tokens |
| **Total** | **~$5-15/month** |

## 🔐 Security

- IAM roles with least-privilege access
- API Gateway with CORS configuration
- No hardcoded credentials (environment variables)
- DynamoDB encryption at rest

## 🛠️ Development

### Local Testing
```bash
# Install dependencies
pip install boto3 requests

# Test analyze function locally
python -c "
import backend.lambda.analyze as a
result = a.fetch_stock_data('AAPL')
print(result)
"
```

### Update Frontend Locally
```bash
cd frontend
python3 -m http.server 3000
# Open http://localhost:3000
```

## 📧 Daily Email Preview

The daily digest includes:
- Current price and change
- Sentiment analysis score
- Technical indicators (RSI, MACD)
- 7-day AI prediction
- Final recommendation
- Unsubscribe link

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

## ⚠️ Disclaimer

**This is for educational purposes only. Not financial advice.**
Always do your own research before making investment decisions.

## 📄 License

MIT License - see LICENSE file for details.

---

Built with ❤️ using AWS Serverless + Amazon Bedrock Claude
