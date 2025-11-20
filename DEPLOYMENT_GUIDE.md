# Cloud Run Deployment Guide

## Where to Run

**Run all commands in your terminal from the project directory:**
```bash
cd /Users/venkateshmallula/workplace/RecognizantForensics 
```

## Prerequisites Checklist

Before deploying, make sure you have:

1. ✅ **Google Cloud Account** with billing enabled
2. ✅ **gcloud CLI installed** and authenticated
   ```bash
   # Check if installed
   gcloud --version
   
   # If not installed, download from:
   # https://cloud.google.com/sdk/docs/install
   
   # Authenticate
   gcloud auth login
   ```

3. ✅ **GCP Project created**
   - Go to: https://console.cloud.google.com/
   - Create a new project or select existing one
   - Note your Project ID

## Step-by-Step Deployment

### Step 1: Set Your GCP Project

```bash
# Replace YOUR_PROJECT_ID with your actual project ID
gcloud config set project YOUR_PROJECT_ID

# Verify it's set
gcloud config get-value project
```

### Step 2: Navigate to Project Directory

```bash
cd /Users/venkateshmallula/workplace/RecognizantForensics 
```

### Step 3: Deploy (Choose One Method)

#### Method A: Using the Deployment Script (Easiest)

```bash
./deploy.sh
```

This script will:
- Check prerequisites
- Enable required APIs
- Build and deploy to Cloud Run
- Show you the service URL

#### Method B: Manual Deployment

```bash
# Set variables
export PROJECT_ID=$(gcloud config get-value project)
export REGION=us-central1

# Enable APIs (first time only)
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    firestore.googleapis.com \
    vision.googleapis.com \
    videointelligence.googleapis.com

# Deploy
gcloud run deploy recognizant-forensics \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10
```

## What Happens During Deployment

1. **Build Phase**: Cloud Build creates a Docker container from your code
2. **Push Phase**: Container is pushed to Google Container Registry
3. **Deploy Phase**: Container is deployed to Cloud Run
4. **URL Generation**: You get a public HTTPS URL

## After Deployment

You'll receive a URL like:
```
https://recognizant-forensics-XXXXX-uc.a.run.app
```

**Access your application** by opening this URL in a browser.

## Verify Deployment

```bash
# Check service status
gcloud run services describe recognizant-forensics \
    --region us-central1 \
    --format 'value(status.url)'

# View logs
gcloud run services logs read recognizant-forensics \
    --region us-central1
```

## Common Issues

### Issue: "gcloud: command not found"
**Solution**: Install Google Cloud SDK
- macOS: `brew install google-cloud-sdk`
- Or download: https://cloud.google.com/sdk/docs/install

### Issue: "Permission denied" when running deploy.sh
**Solution**: Make script executable
```bash
chmod +x deploy.sh
```

### Issue: "Project not found"
**Solution**: Verify project ID
```bash
gcloud projects list
gcloud config set project YOUR_PROJECT_ID
```

### Issue: "Billing not enabled"
**Solution**: Enable billing in GCP Console
- Go to: https://console.cloud.google.com/billing

## Update Deployment

To update your deployment after code changes:

```bash
cd /Users/venkateshmallula/workplace/RecognizantForensics 
./deploy.sh
```

Or manually:
```bash
gcloud run deploy recognizant-forensics \
    --source . \
    --platform managed \
    --region us-central1
```

## Cost Considerations

- **Cloud Run**: Pay per request and compute time
- **Firestore**: Free tier available (1GB storage, 50K reads/day)
- **Vision API**: Pay per API call (check pricing)
- **Video Intelligence API**: Pay per minute processed

For development/testing, costs are typically minimal.

