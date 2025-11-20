#!/bin/bash

# Cloud Run Deployment Script for Recognizant Forensics

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Recognizant Forensics - Cloud Run Deployment${NC}"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI is not installed.${NC}"
    echo "   Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Get project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}⚠️  No project ID set. Please set it:${NC}"
    echo "   gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo -e "${GREEN}✓ Project ID: ${PROJECT_ID}${NC}"

# Get region (default to us-central1)
REGION=${REGION:-us-central1}
echo -e "${GREEN}✓ Region: ${REGION}${NC}"
echo ""

# Service name
SERVICE_NAME="recognizant-forensics"

# Enable required APIs
echo -e "${YELLOW}📦 Enabling required GCP APIs...${NC}"
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    firestore.googleapis.com \
    vision.googleapis.com \
    videointelligence.googleapis.com \
    --project=$PROJECT_ID 2>/dev/null || true

echo -e "${GREEN}✓ APIs enabled${NC}"
echo ""

# Deploy to Cloud Run
echo -e "${YELLOW}🔨 Building and deploying to Cloud Run...${NC}"
echo ""

gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --project $PROJECT_ID

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    echo ""
    echo -e "${GREEN}Your service URL:${NC}"
    gcloud run services describe $SERVICE_NAME \
        --platform managed \
        --region $REGION \
        --project $PROJECT_ID \
        --format 'value(status.url)'
    echo ""
    echo -e "${YELLOW}To view logs:${NC}"
    echo "   gcloud run services logs read $SERVICE_NAME --region $REGION"
    echo ""
else
    echo -e "${RED}❌ Deployment failed${NC}"
    exit 1
fi

