# GitHub Setup and Cloud Run Deployment Guide

This guide will help you:
1. Push your project to GitHub
2. Clone it on any machine
3. Deploy to Cloud Run from the cloned repository

## Step 1: Create GitHub Repository

### Option A: Using GitHub Website

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the **"+"** icon in the top right → **"New repository"**
3. Fill in the details:
   - **Repository name**: `recognizant-forensics` (or your preferred name)
   - **Description**: "Environmental Deepfake Detection - Analyzing environmental inconsistencies in videos"
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
4. Click **"Create repository"**
5. **Copy the repository URL** (you'll need it in the next step)
   - It will look like: `https://github.com/YOUR_USERNAME/recognizant-forensics.git`

### Option B: Using GitHub CLI (if installed)

```bash
gh repo create recognizant-forensics --public --description "Environmental Deepfake Detection"
```

## Step 2: Initialize Git and Push to GitHub

Run these commands in your project directory:

```bash
# Navigate to project directory
cd /Users/venkateshmallula/workplace/RecognizantForensics 

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Recognizant Forensics - Environmental Deepfake Detection"

# Add GitHub remote (replace with your actual repository URL)
git remote add origin https://github.com/YOUR_USERNAME/recognizant-forensics.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

**Note**: If you're prompted for credentials:
- Use a **Personal Access Token** (not your password)
- Create one at: https://github.com/settings/tokens
- Select scopes: `repo` (full control)

## Step 3: Clone from GitHub (On Any Machine)

Once your code is on GitHub, you can clone it anywhere:

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/recognizant-forensics.git

# Navigate into the project
cd recognizant-forensics

# Install dependencies
pip install -r requirements.txt
```

## Step 4: Deploy to Cloud Run from GitHub

### Method 1: Deploy from Local Clone

```bash
# Clone the repository (if not already cloned)
git clone https://github.com/YOUR_USERNAME/recognizant-forensics.git
cd recognizant-forensics

# Run the deployment script
./deploy.sh
```

### Method 2: Deploy Directly from GitHub (Cloud Build)

This method deploys directly from GitHub without cloning locally:

1. **Enable Cloud Build API:**
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   ```

2. **Connect GitHub to Cloud Build:**
   - Go to [Cloud Build Triggers](https://console.cloud.google.com/cloud-build/triggers)
   - Click **"Connect Repository"**
   - Select **GitHub** and authorize
   - Select your repository: `recognizant-forensics`
   - Click **"Connect"**

3. **Create a Trigger:**
   - Click **"Create Trigger"**
   - Name: `deploy-to-cloud-run`
   - Event: **Push to a branch**
   - Branch: `^main$`
   - Configuration: **Cloud Build configuration file**
   - Location: `cloudbuild.yaml`
   - Click **"Create"**

4. **Deploy:**
   - Every push to `main` branch will automatically deploy to Cloud Run
   - Or manually trigger from the Cloud Build console

### Method 3: Deploy from Cloud Shell

1. Open [Google Cloud Shell](https://shell.cloud.google.com/)

2. Clone and deploy:
   ```bash
   # Clone your repository
   git clone https://github.com/YOUR_USERNAME/recognizant-forensics.git
   cd recognizant-forensics
   
   # Set your project
   gcloud config set project YOUR_PROJECT_ID
   
   # Deploy
   ./deploy.sh
   ```

## Step 5: Update Your Code

When you make changes:

```bash
# Make your changes to files

# Stage changes
git add .

# Commit changes
git commit -m "Description of your changes"

# Push to GitHub
git push origin main
```

If you set up Cloud Build triggers, the deployment will happen automatically!

## Quick Reference Commands

### Initial Setup (One Time)
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/recognizant-forensics.git
git branch -M main
git push -u origin main
```

### Daily Workflow
```bash
# Pull latest changes
git pull origin main

# Make changes, then:
git add .
git commit -m "Your commit message"
git push origin main
```

### Clone on New Machine
```bash
git clone https://github.com/YOUR_USERNAME/recognizant-forensics.git
cd recognizant-forensics
pip install -r requirements.txt
```

## Troubleshooting

### "Repository not found"
- Check that the repository URL is correct
- Verify you have access to the repository
- Make sure you're using HTTPS (not SSH) if you haven't set up SSH keys

### "Authentication failed"
- Use a Personal Access Token instead of password
- Create token at: https://github.com/settings/tokens
- Use token as password when prompted

### "Permission denied"
- Make sure you have write access to the repository
- Check repository visibility settings

## Next Steps

After pushing to GitHub:
1. ✅ Your code is backed up and version controlled
2. ✅ You can clone it on any machine
3. ✅ You can deploy to Cloud Run from anywhere
4. ✅ Team members can collaborate
5. ✅ Set up CI/CD for automatic deployments

