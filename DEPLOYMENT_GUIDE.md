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

4. ✅ **Service Account with JSON credentials** (for local testing)
   - See [GCP_CREDENTIALS_SETUP.md](GCP_CREDENTIALS_SETUP.md) for detailed instructions
   - **Important:** You need GCP JSON credentials, NOT AWS CSV credentials
   - For Cloud Run deployment, credentials are handled automatically

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

**Note:** The deployment script works the same as before. Cloud Run automatically uses default service account credentials, so you don't need to set `GOOGLE_APPLICATION_CREDENTIALS` for deployment. (Credentials are only needed for local development/testing.)

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

### Issue: "Vision API not available" or "Firestore not available"
**Solution**: Set up GCP credentials properly
- See [GCP_CREDENTIALS_SETUP.md](GCP_CREDENTIALS_SETUP.md) for detailed instructions
- **Important:** You need GCP JSON credentials, NOT AWS CSV credentials
- Make sure `GOOGLE_APPLICATION_CREDENTIALS` environment variable points to your JSON key file

## Update Deployment (Pull & Redeploy)

To update your Cloud Run deployment after pulling latest code changes:

### Step 1: Pull Latest Code

If your code is in a Git repository (GitHub, etc.):

```bash
# Navigate to project directory
cd /Users/venkateshmallula/workplace/RecognizantForensics 

# Pull latest changes
git pull origin main
# Or: git pull origin master (if using master branch)
```

If you made local changes, you may need to:
```bash
# Stash local changes first
git stash
git pull origin main
git stash pop  # Reapply your local changes
```

### Step 2: Redeploy to Cloud Run

**Option A: Using Deployment Script (Easiest)**
```bash
./deploy.sh
```

**Option B: Manual Deployment**
```bash
# Set your project (if not already set)
gcloud config set project YOUR_PROJECT_ID

# Deploy (this will rebuild and redeploy)
gcloud run deploy recognizant-forensics \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10
```

**Option C: Quick Redeploy (if only code changed, not config)**
```bash
# If you already have a built image
gcloud run deploy recognizant-forensics \
    --image gcr.io/YOUR_PROJECT_ID/recognizant-forensics \
    --platform managed \
    --region us-central1
```

### Step 3: Verify Deployment

After deployment, verify it's running:
```bash
# Check service status
gcloud run services describe recognizant-forensics \
    --region us-central1 \
    --format 'value(status.url)'

# View recent logs
gcloud run services logs read recognizant-forensics \
    --region us-central1 \
    --limit 50
```

### Complete Workflow Example

```bash
# 1. Navigate to project
cd /Users/venkateshmallula/workplace/RecognizantForensics 

# 2. Pull latest code
git pull origin main

# 3. Deploy
./deploy.sh

# 4. Verify (optional)
gcloud run services describe recognizant-forensics \
    --region us-central1 \
    --format 'value(status.url)'
```

### Restart Cloud Run Service (Without Code Changes)

If you just need to restart the service (e.g., after a crash):

```bash
# Restart by updating with same configuration
gcloud run services update recognizant-forensics \
    --region us-central1 \
    --no-traffic \
    --platform managed

# Then route traffic back
gcloud run services update-traffic recognizant-forensics \
    --region us-central1 \
    --to-latest
```

Or simply redeploy (which restarts the service):
```bash
./deploy.sh
```

## Cost Considerations

- **Cloud Run**: Pay per request and compute time
- **Firestore**: Free tier available (1GB storage, 50K reads/day)
- **Vision API**: Pay per API call (check pricing)
- **Video Intelligence API**: Pay per minute processed

For development/testing, costs are typically minimal.

