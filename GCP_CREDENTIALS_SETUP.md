# GCP Credentials Setup Guide

## Important: This Project Uses Google Cloud Platform (GCP), Not AWS

**Note:** If you have AWS credentials (CSV format with Access Key ID and Secret Access Key), those are for AWS services. This project requires **Google Cloud Platform (GCP) credentials** in **JSON format**.

## Step-by-Step: Getting GCP Credentials

### Step 1: Create a GCP Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click "New Project"
4. Enter a project name (e.g., "recognizant-forensics")
5. Click "Create"
6. Wait for the project to be created and select it

### Step 2: Enable Required APIs

1. Go to [APIs & Services > Library](https://console.cloud.google.com/apis/library)
2. Search for and enable each of these APIs:
   - **Cloud Vision API**
   - **Cloud Firestore API**
   - **Cloud Run API** (for deployment)
   - **Cloud Build API** (for deployment)

Or use the command line:
```bash
gcloud services enable \
    vision.googleapis.com \
    firestore.googleapis.com \
    run.googleapis.com \
    cloudbuild.googleapis.com
```

### Step 3: Create a Service Account

1. Go to [IAM & Admin > Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Click "Create Service Account"
3. Enter a name: `recognizant-forensics-service`
4. Click "Create and Continue"

### Step 4: Grant Required Permissions

Add these roles to your service account:
- **Cloud Vision API User** - For Vision API access
- **Cloud Datastore User** - For Firestore access

Click "Continue" then "Done"

### Step 5: Create and Download JSON Key

1. Click on the service account you just created
2. Go to the "Keys" tab
3. Click "Add Key" → "Create new key"
4. Select **JSON** format (NOT CSV)
5. Click "Create"
6. The JSON file will download automatically

**Important:** The file will be named something like:
```
your-project-name-xxxxx-xxxxxxxxxxxx.json
```

### Step 6: Set Up Credentials

**For Local Development:**

1. Move the downloaded JSON file to a secure location:
   ```bash
   mv ~/Downloads/your-project-name-xxxxx-xxxxxxxxxxxx.json ~/.gcp/recognizant-credentials.json
   ```

2. Set the environment variable:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.gcp/recognizant-credentials.json"
   ```

3. Add to your shell profile (for persistence):
   ```bash
   # For bash
   echo 'export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.gcp/recognizant-credentials.json"' >> ~/.bashrc
   
   # For zsh
   echo 'export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.gcp/recognizant-credentials.json"' >> ~/.zshrc
   ```

4. Verify it's set:
   ```bash
   echo $GOOGLE_APPLICATION_CREDENTIALS
   ```

**For Cloud Run Deployment:**

No credentials file needed! Cloud Run automatically uses the service account attached to the service. Just make sure the service account has the required permissions (done in Step 4).

### Step 7: Verify Setup

Run the application:
```bash
python app.py
```

You should see:
```
✓ Google Vision API initialized successfully
✓ Firestore initialized successfully
```

If you see warnings instead, check:
1. The JSON file path is correct
2. The environment variable is set
3. The service account has the right permissions
4. The APIs are enabled

## Troubleshooting

### Issue: "Could not initialize Vision API: [Errno 2] No such file or directory"
**Solution:** The credentials file path is incorrect. Check:
```bash
ls -la $GOOGLE_APPLICATION_CREDENTIALS
```

### Issue: "Permission denied" or "403 Forbidden"
**Solution:** The service account doesn't have the right permissions. Go back to Step 4 and add the required roles.

### Issue: "API not enabled"
**Solution:** Enable the APIs in Step 2.

### Issue: "Billing not enabled"
**Solution:** 
1. Go to [Billing](https://console.cloud.google.com/billing)
2. Link a billing account to your project
3. Note: Vision API and Firestore have free tiers, but billing must be enabled

## Security Best Practices

1. **Never commit credentials to Git:**
   - Add `*.json` to `.gitignore`
   - Add `venkateshmallula_accessKeys.csv` to `.gitignore` (if you have AWS keys)

2. **Use different service accounts for different environments:**
   - One for development
   - One for production

3. **Rotate keys regularly:**
   - Delete old keys from the service account
   - Create new keys when needed

4. **Limit permissions:**
   - Only grant the minimum required permissions
   - Don't use "Owner" or "Editor" roles

## Difference: AWS vs GCP Credentials

| AWS | GCP |
|-----|-----|
| CSV format | JSON format |
| Access Key ID + Secret | Service Account JSON |
| Used for AWS services | Used for GCP services |
| Example: `AKIA...` | Example: `{"type": "service_account", ...}` |

**This project uses GCP, so you need GCP JSON credentials, not AWS CSV credentials.**

