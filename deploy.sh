#!/bin/bash
# ============================================================
# StockPulse AI - AWS Deployment Script
# ============================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        StockPulse AI - AWS Deployment Script           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo

# Configuration
STACK_NAME="stockpulse-ai"
REGION="${AWS_REGION:-us-east-2}"
ENVIRONMENT="prod"

# Check for required environment variables
if [ -z "$ALPHA_VANTAGE_KEY" ]; then
    echo -e "${YELLOW}Warning: ALPHA_VANTAGE_KEY not set. Get free key at: https://www.alphavantage.co/support/#api-key${NC}"
    read -p "Enter Alpha Vantage API Key: " ALPHA_VANTAGE_KEY
fi

if [ -z "$NEWS_API_KEY" ]; then
    echo -e "${YELLOW}Warning: NEWS_API_KEY not set. Get free key at: https://newsapi.org/${NC}"
    read -p "Enter News API Key (or press Enter to skip): " NEWS_API_KEY
fi

if [ -z "$SENDER_EMAIL" ]; then
    echo -e "${YELLOW}Warning: SENDER_EMAIL not set for SES${NC}"
    read -p "Enter verified SES email (or press Enter to skip): " SENDER_EMAIL
    SENDER_EMAIL="${SENDER_EMAIL:-noreply@example.com}"
fi

echo -e "\n${GREEN}Step 1: Packaging Lambda functions...${NC}"
cd backend/lambda

# Create deployment packages
for func in subscribe unsubscribe analyze daily_digest; do
    if [ -f "${func}.py" ]; then
        echo "  Packaging ${func}..."
        zip -q "${func}.zip" "${func}.py" 2>/dev/null || true
    fi
done
cd ../..

echo -e "\n${GREEN}Step 2: Deploying CloudFormation stack...${NC}"
aws cloudformation deploy \
    --template-file infrastructure/template.yaml \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --capabilities CAPABILITY_NAMED_IAM \
    --parameter-overrides \
        Environment="$ENVIRONMENT" \
        AlphaVantageApiKey="$ALPHA_VANTAGE_KEY" \
        NewsApiKey="${NEWS_API_KEY:-none}" \
        SenderEmail="$SENDER_EMAIL" \
    --no-fail-on-empty-changeset

echo -e "\n${GREEN}Step 3: Getting stack outputs...${NC}"
API_URL=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
    --output text)

BUCKET_NAME=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`FrontendBucketName`].OutputValue' \
    --output text)

WEBSITE_URL=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`WebsiteURL`].OutputValue' \
    --output text)

echo -e "\n${GREEN}Step 4: Updating Lambda function code...${NC}"
cd backend/lambda
for func in subscribe unsubscribe analyze daily_digest; do
    if [ -f "${func}.zip" ]; then
        echo "  Deploying ${func}..."
        aws lambda update-function-code \
            --function-name "stockpulse-${func//_/-}-${ENVIRONMENT}" \
            --zip-file "fileb://${func}.zip" \
            --region "$REGION" 2>/dev/null || echo "  (Function may need initial deployment)"
    fi
done
cd ../..

echo -e "\n${GREEN}Step 5: Updating frontend with API URL...${NC}"
sed -i "s|YOUR_API_GATEWAY_URL|${API_URL}|g" frontend/index.html

echo -e "\n${GREEN}Step 6: Deploying frontend to S3...${NC}"
aws s3 sync frontend/ "s3://${BUCKET_NAME}/" \
    --region "$REGION" \
    --delete \
    --content-type "text/html" \
    --exclude "*" --include "*.html"

aws s3 sync frontend/ "s3://${BUCKET_NAME}/" \
    --region "$REGION" \
    --exclude "*.html"

echo
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              Deployment Complete!                       ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo
echo -e "${BLUE}Website URL:${NC}  $WEBSITE_URL"
echo -e "${BLUE}API URL:${NC}      $API_URL"
echo
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Verify your sender email in SES (if not done)"
echo "2. Request SES production access for sending to any email"
echo "3. Enable Bedrock Claude model access in AWS Console"
echo
