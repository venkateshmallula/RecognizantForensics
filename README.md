# Recognizant Forensics - Environmental Deepfake Detection

A novel approach to deepfake detection that analyzes environmental inconsistencies in videos rather than facial features.

## Features

- **Audio Reverb Analysis**: Detects acoustic inconsistencies that indicate artificial audio manipulation
- **Shadow Consistency Checking**: Analyzes shadow patterns across video frames for physics violations
- **Reflection Detection**: Uses Vision API to detect inconsistent reflections in reflective surfaces
- **Combined Scoring**: Weighted algorithm that combines multiple detection vectors

## Local Setup

### Prerequisites

1. **Python 3.10+** (tested with Python 3.13)
2. **ffmpeg** (required for audio extraction)
   ```bash
   # macOS
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt-get install ffmpeg
   
   # Windows
   # Download from https://ffmpeg.org/download.html
   ```

### Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Optional: GCP Setup (for Vision API and Firestore)**
   - Create a GCP project
   - Enable Vision API and Firestore
   - Download service account JSON key
   - Set environment variable:
     ```bash
     export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
     ```
   - Note: The application will work without GCP credentials, but some features will be limited

### Running Locally

1. **Start the Flask server:**
   ```bash
   python app.py
   ```

2. **Access the application:**
   Open your browser and navigate to: `http://localhost:8080`

3. **Upload a video:**
   - Click or drag-and-drop a video file
   - Wait for analysis to complete
   - View results with confidence score and findings

## Project Structure

```
RecognizantForensics/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── analyzer/
│   ├── __init__.py
│   ├── audio_checker.py  # Reverb analysis
│   ├── visual_checker.py # Shadow/reflection analysis
│   └── scorer.py         # Combine results
├── static/
│   ├── index.html        # Upload UI
│   └── style.css         # Styling
└── test_videos/          # Place test videos here
```

## How It Works

1. **Audio Analysis**: Extracts audio track and analyzes reverb patterns, silence ratios, and acoustic properties
2. **Visual Analysis**: Samples frames to check shadow consistency and detect reflection anomalies
3. **Scoring**: Combines audio (60% weight) and visual (40% weight) scores into final verdict
4. **Results**: Displays confidence score, verdict, and key findings

## Cloud Run Deployment

### Prerequisites

1. **Google Cloud Project** with billing enabled
2. **gcloud CLI** installed and authenticated
3. **Docker** (optional, for local testing)

### Setup GCP Services

1. **Enable required APIs:**
   ```bash
   gcloud services enable \
       cloudbuild.googleapis.com \
       run.googleapis.com \
       firestore.googleapis.com \
       vision.googleapis.com \
       videointelligence.googleapis.com
   ```

2. **Create Firestore database** (if not exists):
   ```bash
   gcloud firestore databases create --region=us-central
   ```

3. **Set up service account** (Cloud Run uses default compute service account):
   ```bash
   # Grant necessary permissions
   gcloud projects add-iam-policy-binding PROJECT_ID \
       --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
       --role="roles/datastore.user"
   
   gcloud projects add-iam-policy-binding PROJECT_ID \
       --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
       --role="roles/vision.annotator"
   ```

### Deploy to Cloud Run

**Option 1: Deploy from source (Recommended)**
```bash
# Set your project ID
export PROJECT_ID=your-project-id
export REGION=us-central1

# Deploy to Cloud Run
gcloud run deploy recognizant-forensics \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --set-env-vars PORT=8080
```

**Option 2: Build and deploy with Docker**
```bash
# Build the container
gcloud builds submit --tag gcr.io/$PROJECT_ID/recognizant-forensics

# Deploy to Cloud Run
gcloud run deploy recognizant-forensics \
    --image gcr.io/$PROJECT_ID/recognizant-forensics \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300
```

### Configuration Options

- **Memory**: 2Gi recommended (can be increased for larger videos)
- **CPU**: 2 recommended for faster processing
- **Timeout**: 300 seconds (5 minutes) for video processing
- **Max Instances**: Adjust based on expected load
- **Concurrency**: Default is 80 requests per instance

### Access Your Deployment

After deployment, Cloud Run will provide a URL:
```
https://recognizant-forensics-XXXXX-uc.a.run.app
```

### Update Deployment

```bash
gcloud run deploy recognizant-forensics \
    --source . \
    --platform managed \
    --region $REGION
```

## Notes

- The application works both locally and on Cloud Run
- GCP services (Vision API, Firestore) are automatically available on Cloud Run
- Cloud Run automatically handles scaling and load balancing
- Video processing may take time; ensure timeout is set appropriately
- If ffmpeg is not installed, audio analysis will fail gracefully
- If librosa is not available, basic audio analysis will be used as fallback

## Troubleshooting

- **"ffmpeg not found"**: Install ffmpeg (see Prerequisites)
- **"librosa not available"**: Install librosa: `pip install librosa`
- **Vision API errors**: Ensure GCP credentials are set correctly, or the app will use fallback detection
- **Port already in use**: Change port in `app.py` from 8080 to another port

## License

This project was created for a hackathon demonstration.

