# Recognizant Forensics - Environmental Deepfake Detection

A novel approach to deepfake detection that analyzes environmental inconsistencies in videos rather than facial features.

## Features

- **Audio Reverb Analysis**: Detects acoustic inconsistencies that indicate artificial audio manipulation
- **Shadow Consistency Checking**: Analyzes shadow patterns across video frames for physics violations
- **Reflection Detection**: Uses Vision API to detect inconsistent reflections in reflective surfaces
- **Combined Scoring**: Weighted algorithm that combines multiple detection vectors

## Application Use Case

### Abstract

Recognizant Forensics is a web-based deepfake detection application that employs an innovative environmental analysis approach to identify manipulated video content. Unlike traditional facial recognition-based detection methods, this application focuses on analyzing the **background environment** of videos—examining environmental inconsistencies such as audio reverb patterns, shadow physics, and reflection anomalies that are computationally expensive and difficult for deepfake generators to replicate accurately.

**An estimated 8 million deepfakes are projected to be shared online in 2025, a massive increase from approximately 500,000 in 2023.** This exponential growth in synthetic media makes reliable, automated detection tools critical for maintaining trust in digital content across news media, social platforms, legal proceedings, and corporate communications.

### Core Functionality

The application provides a RESTful web service that accepts video uploads and returns comprehensive authenticity analysis through the following workflow:

1. **Video Upload & Processing**: Users upload video files through a web interface, which are temporarily stored and processed server-side.

2. **Multi-Modal Analysis Pipeline** (Background Environment Focus):
   - **Audio Reverb Analysis**: Extracts the audio track from the video and analyzes acoustic properties including reverb patterns, silence ratios, and frequency characteristics. Authentic recordings exhibit consistent reverb signatures that reflect the physical recording environment (background acoustic space), while deepfakes often show acoustic inconsistencies in the environmental audio.
   - **Visual Consistency Checking**: Samples video frames at strategic intervals to analyze shadow patterns in the background environment for physics violations. Real-world shadows in the background must be consistent with lighting sources and object positions, while synthetic content frequently contains shadow anomalies in environmental elements.
   - **Reflection Detection**: Leverages Google Cloud Vision API to detect and analyze reflections in background elements such as mirrors, windows, and other reflective surfaces. Inconsistent reflections in the background environment reveal spatial relationship violations that indicate manipulation.

3. **Intelligent Scoring System**: Combines analysis results using a weighted algorithm (60% audio, 40% visual) to generate a confidence score and verdict:
   - **LIKELY AUTHENTIC** (score ≥ 80): High confidence the video is genuine
   - **SUSPICIOUS** (score 50-79): Medium confidence with detected anomalies
   - **LIKELY DEEPFAKE** (score < 50): High confidence the video is manipulated

4. **Results Presentation**: Returns detailed JSON response containing:
   - Final confidence score and verdict
   - Key indicators and findings from each analysis module
   - Technical details (reverb coefficients, shadow variance metrics)
   - Optional storage in Google Cloud Firestore for audit trails

5. **Scalable Architecture**: Designed for deployment on Google Cloud Run, enabling automatic scaling to handle concurrent video analysis requests with configurable resource allocation (memory, CPU, timeout settings).

The application serves as a critical tool for content verification, helping organizations and individuals make informed decisions about video authenticity in an era of rapidly advancing synthetic media technology.

## High Level Design

Recognizant Forensics follows a layered, modular architecture designed for scalability, maintainability, and cloud deployment. The system is built on a client-server model with a RESTful API backend and a web-based frontend, enabling asynchronous video processing and real-time result delivery.

### Architecture Overview

The application is structured in four primary layers: **Presentation Layer**, **Application Layer**, **Analysis Layer**, and **Data Layer**. The Presentation Layer consists of a static HTML/CSS frontend that provides a user-friendly interface for video uploads and result visualization. The Application Layer is implemented as a Flask-based REST API server that handles HTTP requests, manages file uploads, orchestrates the analysis pipeline, and returns JSON-formatted results. The Analysis Layer contains modular components for audio and visual analysis, each operating independently to enable parallel processing and easy extensibility. The Data Layer integrates with Google Cloud Firestore for optional result persistence and leverages Google Cloud Vision API for advanced reflection detection capabilities.

### Component Architecture

The system is organized into discrete, loosely-coupled modules that communicate through well-defined interfaces. The main Flask application (`app.py`) serves as the orchestration engine, receiving video uploads through the `/analyze` endpoint and coordinating the analysis workflow. The analyzer package contains three specialized modules: `audio_checker.py` handles audio extraction and reverb analysis using ffmpeg and librosa, `visual_checker.py` performs shadow consistency checking and reflection detection using OpenCV and Google Vision API, and `scorer.py` implements the weighted scoring algorithm that combines results from both analysis modules. Each module is designed with graceful degradation—the system continues to function even if optional dependencies (librosa, Vision API) are unavailable, falling back to simpler analysis methods.

### Data Flow

The processing pipeline follows a sequential workflow optimized for background environment analysis. When a video is uploaded, it is temporarily stored in the system's temporary directory. The audio analysis module extracts the audio track using ffmpeg, converting it to a WAV format for processing. The audio is then analyzed for reverb patterns, spectral characteristics, and silence ratios that indicate environmental acoustic inconsistencies. Simultaneously, the visual analysis module samples frames at strategic intervals (typically 5 evenly-spaced frames) to analyze shadow patterns and detect reflection anomalies. The visual checker uses computer vision techniques to identify shadow direction consistency across frames and leverages Google Cloud Vision API to detect reflective surfaces and analyze their content. Both analysis modules return structured results containing scores (0-100), findings lists, and technical metrics. The scorer module then combines these results using a weighted algorithm (60% audio, 40% visual) to generate a final confidence score and verdict. The results are formatted as JSON and returned to the client, with optional storage in Firestore for audit trails. Temporary files are automatically cleaned up after processing to manage storage efficiently.

### Technology Stack

The application is built on Python 3.10+ using Flask as the web framework and Gunicorn as the production WSGI server. Audio processing leverages ffmpeg for extraction and librosa for advanced spectral analysis, with fallback support using scipy and numpy for basic audio analysis. Visual processing uses OpenCV for frame extraction, shadow detection, and image manipulation. Google Cloud Vision API provides advanced object detection and reflection analysis capabilities. The system integrates with Google Cloud Firestore for optional result persistence and is containerized using Docker for consistent deployment across environments. The application is designed for deployment on Google Cloud Run, which provides automatic scaling, load balancing, and serverless infrastructure management.

### Integration Points

The system integrates with external services through well-defined interfaces that support optional operation. Google Cloud Vision API integration is implemented with try-except error handling, allowing the application to function with basic reflection detection if the API is unavailable. Firestore integration follows a similar pattern, with the application storing analysis results when credentials are available but continuing to operate normally when they are not. This design enables local development and testing without requiring full GCP setup, while still leveraging cloud services in production environments. The ffmpeg dependency is required for audio extraction, but the system provides clear error messages if it is not installed.

### Scalability and Performance

The architecture is designed for horizontal scaling through stateless request handling and cloud-native deployment patterns. Each analysis request is independent and can be processed in parallel across multiple Cloud Run instances. The system uses temporary file storage that is automatically cleaned up, preventing storage accumulation. Resource allocation is configurable through Cloud Run settings (memory, CPU, timeout), allowing optimization for different video sizes and processing requirements. The modular design enables future enhancements such as distributed processing, caching mechanisms, or additional analysis modules without requiring architectural changes. The weighted scoring system allows fine-tuning of detection sensitivity by adjusting the audio/visual weight ratios, and the threshold values for verdict classification can be calibrated based on validation datasets.

## Sample Dataset / Artifacts Description

### Test Video Requirements

For effective testing and validation of Recognizant Forensics, sample videos should include diverse scenarios that test the system's ability to detect environmental inconsistencies. Test videos should be placed in the `test_videos/` directory and should include:

**Authentic Video Characteristics:**
- Videos recorded in natural environments with consistent background elements
- Clear audio tracks with natural reverb patterns matching the visible space
- Consistent shadow patterns across frames that align with lighting sources
- Reflective surfaces (mirrors, windows, glasses) showing consistent environmental reflections
- Various recording environments: indoor rooms, outdoor spaces, studios, offices
- Multiple video formats: MP4, AVI, MOV, MKV
- Duration: 5 seconds to 5 minutes (optimal range for analysis)

**Deepfake Video Characteristics (for validation):**
- Videos with manipulated audio tracks showing inconsistent reverb patterns
- Videos with shadow anomalies in background elements
- Videos with inconsistent reflections in mirrors or windows
- Videos where background environment doesn't match audio acoustic properties
- Videos with unnatural silence patterns or audio gaps
- Videos with physics violations in environmental elements

### Recommended Datasets

While the `test_videos/` directory is provided for custom test videos, the following public datasets can be used for validation:

1. **FaceForensics++**: Contains both authentic and deepfake videos with various manipulation techniques
2. **DFDC (Deepfake Detection Challenge)**: Large-scale dataset with diverse deepfake generation methods
3. **Celeb-DF**: High-quality deepfake videos with corresponding authentic source videos
4. **WildDeepfake**: Real-world deepfake videos collected from the internet
5. **Custom Recordings**: User-generated authentic videos in controlled environments with known acoustic and lighting properties

### System Artifacts and Outputs

The application generates several artifacts during the analysis process:

**Temporary Processing Artifacts:**
- **Extracted Audio Files**: WAV format audio tracks extracted from videos (stored temporarily, auto-deleted after analysis)
- **Sampled Frame Images**: Selected video frames used for visual analysis (processed in memory, not persisted)
- **Temporary Video Files**: Uploaded videos stored temporarily in system temp directory during processing

**Analysis Results (JSON Format):**
```json
{
  "success": true,
  "analysis": {
    "score": 75.5,
    "verdict": "SUSPICIOUS",
    "confidence": "Medium confidence",
    "key_indicators": [
      "Reverb pattern inconsistent with visible space",
      "Shadow angles inconsistent between frames"
    ],
    "technical_details": {
      "audio_reverb": 4500.0,
      "shadow_variance": 0.65
    }
  },
  "details": {
    "audio": [
      "Reverb pattern inconsistent with visible space",
      "Unnatural silence patterns detected"
    ],
    "visual": [
      "Shadow angles inconsistent between frames",
      "Multiple reflection-like patterns detected"
    ]
  }
}
```

**Firestore Database Artifacts (Optional):**
When Firestore is configured, the system stores analysis records with the following structure:
- **Collection**: `analyses`
- **Document Fields**:
  - `filename`: Original video filename
  - `audio_score`: Audio analysis score (0-100)
  - `visual_score`: Visual analysis score (0-100)
  - `final_verdict`: Classification result (LIKELY AUTHENTIC, SUSPICIOUS, LIKELY DEEPFAKE)
  - `timestamp`: Server timestamp of analysis

**Technical Metrics:**
- **Audio Reverb Coefficient**: Spectral rolloff mean value indicating acoustic space characteristics
- **Shadow Variance**: Variance in shadow angle measurements across sampled frames
- **Silence Ratio**: Proportion of audio track with minimal amplitude
- **Frame Sample Indices**: Positions of frames analyzed (typically 5 evenly-spaced frames)

### Validation and Testing

For comprehensive testing, create a test suite with:
- **Positive Cases**: Known authentic videos that should score ≥ 80
- **Negative Cases**: Known deepfake videos that should score < 50
- **Edge Cases**: Videos with poor quality, unusual lighting, or minimal background elements
- **Boundary Cases**: Videos scoring near threshold boundaries (50, 80) to test classification accuracy

The system's scoring thresholds can be calibrated based on validation results from these datasets to optimize detection accuracy for specific use cases.

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

2. **GCP Setup (Required for Vision API and Firestore)**
   
   **Important:** This project uses **Google Cloud Platform (GCP)**, not AWS. You need **GCP credentials in JSON format**, not AWS CSV credentials.
   
   **Quick Setup:**
   
   a. Create a GCP project at https://console.cloud.google.com/
   
   b. Enable required APIs:
   ```bash
   gcloud services enable \
       vision.googleapis.com \
       firestore.googleapis.com
   ```
   
   c. Create a service account and download JSON key:
   - Go to [IAM & Admin > Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
   - Create new service account
   - Grant roles: **"Cloud Vision API User"** and **"Cloud Datastore User"**
   - Create and download **JSON key** (NOT CSV)
   
   d. Set credentials:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-service-account-key.json"
   ```
   
   e. Verify setup:
   ```bash
   python app.py
   # Should see: "✓ Google Vision API initialized successfully"
   # Should see: "✓ Firestore initialized successfully"
   ```
   
   **📖 For detailed step-by-step instructions, see [GCP_CREDENTIALS_SETUP.md](GCP_CREDENTIALS_SETUP.md)**
   
   **Note:** The application will work without GCP credentials, but Vision API reflection detection and Firestore storage will be disabled.

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
├── GCP_CREDENTIALS_SETUP.md  # GCP credentials setup guide
├── DEPLOYMENT_GUIDE.md   # Cloud Run deployment guide
├── deploy.sh             # Initial deployment script
├── update_deployment.sh  # Pull & redeploy script
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

