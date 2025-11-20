from flask import Flask, request, jsonify, send_from_directory
import tempfile
import os
from analyzer import audio_checker, visual_checker, scorer

# Optional GCP imports - will work without them for local testing
try:
    from google.cloud import firestore
    db = firestore.Client()
    HAS_FIRESTORE = True
except Exception:
    db = None
    HAS_FIRESTORE = False
    print("Warning: Firestore not available. Results won't be stored in database.")

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    """Serve the main upload page"""
    html_path = os.path.join('static', 'index.html')
    if os.path.exists(html_path):
        return open(html_path).read()
    else:
        return "HTML file not found. Please ensure static/index.html exists."

@app.route('/<path:filename>')
def static_files(filename):
    """Serve static files (CSS, JS, etc.)"""
    return send_from_directory(app.static_folder, filename)

@app.route('/analyze', methods=['POST'])
def analyze_video():
    """Analyze uploaded video for deepfake indicators"""
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        video_file = request.files['video']
        if video_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file to temp location
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, video_file.filename)
        video_file.save(temp_path)
        
        print(f"Processing video: {temp_path}")
        
        # Extract audio track and analyze reverb
        print("Analyzing audio reverb patterns...")
        audio_results = audio_checker.check_reverb(temp_path)
        
        # Get video frames for visual analysis
        print("Analyzing visual consistency...")
        visual_results = visual_checker.check_shadows(temp_path)
        
        # Combine scores
        print("Calculating final confidence score...")
        final_score = scorer.calculate_confidence(audio_results, visual_results)
        
        # Store in Firestore if available (optional for local)
        if HAS_FIRESTORE and db:
            try:
                doc_ref = db.collection('analyses').add({
                    'filename': video_file.filename,
                    'audio_score': audio_results['score'],
                    'visual_score': visual_results['score'],
                    'final_verdict': final_score['verdict'],
                    'timestamp': firestore.SERVER_TIMESTAMP
                })
                print("Results stored in Firestore")
            except Exception as e:
                print(f"Warning: Could not store in Firestore: {e}")
        
        # Clean up temp file
        try:
            os.remove(temp_path)
        except:
            pass
        
        return jsonify({
            'success': True,
            'analysis': final_score,
            'details': {
                'audio': audio_results['findings'],
                'visual': visual_results['findings']
            }
        })
        
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback.print_exc()
        return jsonify({'error': error_msg}), 500

if __name__ == '__main__':
    # For local development
    port = int(os.environ.get('PORT', 8080))
    print(f"Starting Recognizant Forensics server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)
else:
    # For Cloud Run / production (gunicorn)
    port = int(os.environ.get('PORT', 8080))
    print(f"Starting Recognizant Forensics server on port {port}...")

