import cv2
import numpy as np
import os

# Configuration - can be overridden via environment variables
SHADOW_THRESHOLD = int(os.environ.get('SHADOW_THRESHOLD', 50))
SHADOW_VARIANCE_THRESHOLD = float(os.environ.get('SHADOW_VARIANCE_THRESHOLD', 0.5))
BRIGHT_THRESHOLD = int(os.environ.get('BRIGHT_THRESHOLD', 200))
BRIGHT_RATIO_MIN = float(os.environ.get('BRIGHT_RATIO_MIN', 0.05))
BRIGHT_RATIO_MAX = float(os.environ.get('BRIGHT_RATIO_MAX', 0.3))
CONTOUR_COUNT_THRESHOLD = int(os.environ.get('CONTOUR_COUNT_THRESHOLD', 5))
FRAME_SAMPLE_COUNT = int(os.environ.get('FRAME_SAMPLE_COUNT', 5))

# Reflective objects to detect - can be extended via config
REFLECTIVE_OBJECTS = os.environ.get('REFLECTIVE_OBJECTS', 
    'Glasses,Computer monitor,Television,Mirror,Window').split(',')

# Initialize GCP Vision API with proper credential handling
vision_client = None
HAS_VISION_API = False

try:
    from google.cloud import vision
    from google.auth import default
    from google.auth.exceptions import DefaultCredentialsError
    
    # Try to get credentials
    try:
        credentials, project = default()
        vision_client = vision.ImageAnnotatorClient(credentials=credentials)
        HAS_VISION_API = True
        print("✓ Google Vision API initialized successfully")
    except DefaultCredentialsError:
        # Check if credentials file is specified
        creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if creds_path and os.path.exists(creds_path):
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
            vision_client = vision.ImageAnnotatorClient()
            HAS_VISION_API = True
            print("✓ Google Vision API initialized with credentials file")
        else:
            print("⚠ Warning: Google Vision API credentials not found.")
            print("  Set GOOGLE_APPLICATION_CREDENTIALS environment variable or")
            print("  ensure you're running on GCP with default credentials.")
            print("  Reflection detection will use fallback method.")
except ImportError:
    print("⚠ Warning: google-cloud-vision not installed. Install with: pip install google-cloud-vision")
except Exception as e:
    print(f"⚠ Warning: Could not initialize Vision API: {e}")
    print("  Reflection detection will use fallback method.")

def check_shadows(video_path):
    """Check shadow consistency across frames"""
    
    if not os.path.exists(video_path):
        return {
            'score': 50,
            'findings': ['Video file not found'],
            'shadow_variance': 0
        }
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {
            'score': 50,
            'findings': ['Could not open video file'],
            'shadow_variance': 0
        }
    
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if frame_count == 0:
        cap.release()
        return {
            'score': 50,
            'findings': ['Video has no frames'],
            'shadow_variance': 0
        }
    
    # Sample frames evenly (configurable count)
    sample_count = min(FRAME_SAMPLE_COUNT, frame_count)
    sample_frames = np.linspace(0, frame_count-1, sample_count, dtype=int)
    shadow_angles = []
    findings = []
    score = 100
    
    for frame_idx in sample_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret:
            continue
        
        # Convert to grayscale for shadow detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Simple shadow detection using threshold (configurable)
        # Look for dark regions that could be shadows
        _, shadow_mask = cv2.threshold(gray, SHADOW_THRESHOLD, 255, cv2.THRESH_BINARY_INV)
        
        # Find primary shadow direction (using moments)
        moments = cv2.moments(shadow_mask)
        if moments['m00'] > 0:
            cx = moments['m10'] / moments['m00']
            cy = moments['m01'] / moments['m00']
            
            # Calculate angle from center
            center_x = frame.shape[1] / 2
            center_y = frame.shape[0] / 2
            angle = np.arctan2(cy - center_y, cx - center_x)
            shadow_angles.append(angle)
    
    # Check if shadows jumped impossibly (configurable threshold)
    if len(shadow_angles) > 1:
        angle_variance = np.var(shadow_angles)
        if angle_variance > SHADOW_VARIANCE_THRESHOLD:
            findings.append("Shadow angles inconsistent between frames")
            score -= 35
    
    # Bonus: Check for reflection in glasses/screens using Vision API
    if frame_count > 0:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count // 2)
        ret, middle_frame = cap.read()
        if ret:
            reflection_check = detect_reflections(middle_frame)
            if reflection_check['suspicious']:
                findings.append(reflection_check['message'])
                score -= 30
    
    cap.release()
    
    return {
        'score': max(0, score),
        'findings': findings if findings else ["Visual elements appear consistent"],
        'shadow_variance': float(angle_variance) if len(shadow_angles) > 1 else 0
    }

def detect_reflections(frame):
    """Reflection detection using Vision API with enhanced analysis, fallback to image analysis"""
    
    if HAS_VISION_API and vision_client:
        try:
            # Convert frame to bytes
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
            image = vision.Image(content=buffer.tobytes())
            
            # Use Vision API to detect objects and analyze reflections
            response = vision_client.object_localization(image=image)
            objects = response.localized_object_annotations
            
            # Check for reflective objects (configurable list)
            detected_reflective = []
            for obj in objects:
                obj_name_lower = obj.name.lower()
                for ref_obj in REFLECTIVE_OBJECTS:
                    if ref_obj.lower() in obj_name_lower or obj_name_lower in ref_obj.lower():
                        detected_reflective.append({
                            'name': obj.name,
                            'confidence': obj.score,
                            'bounding_poly': obj.bounding_poly
                        })
            
            if detected_reflective:
                # Analyze reflection content using Vision API's safe search and properties
                try:
                    # Get image properties for reflection analysis
                    properties_response = vision_client.image_properties(image=image)
                    dominant_colors = properties_response.image_properties_annotation.dominant_colors.colors
                    
                    # Check for suspicious color patterns that might indicate manipulation
                    # Reflections should have consistent color properties
                    if len(dominant_colors) > 0:
                        # Analyze color distribution
                        color_variance = np.var([color.score for color in dominant_colors[:5]])
                        
                        return {
                            'suspicious': True,
                            'message': f"Reflection detected in {detected_reflective[0]['name'].lower()} with color variance: {color_variance:.2f}",
                            'detected_objects': [obj['name'] for obj in detected_reflective],
                            'vision_api_used': True
                        }
                except Exception as e:
                    print(f"Vision API properties analysis error: {e}")
                    # Still report reflective object detection
                    return {
                        'suspicious': True,
                        'message': f"Reflection detected in {detected_reflective[0]['name'].lower()}",
                        'detected_objects': [obj['name'] for obj in detected_reflective],
                        'vision_api_used': True
                    }
        except Exception as e:
            print(f"Vision API error: {e}")
            print("  Falling back to basic image analysis...")
            # Fall through to basic detection
    
    # Fallback: Basic reflection detection using image analysis (configurable thresholds)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, bright_mask = cv2.threshold(gray, BRIGHT_THRESHOLD, 255, cv2.THRESH_BINARY)
    
    # Count bright regions
    bright_pixels = np.sum(bright_mask > 0)
    total_pixels = frame.shape[0] * frame.shape[1]
    bright_ratio = bright_pixels / total_pixels
    
    # If there are many small bright regions, might be reflections (configurable thresholds)
    if BRIGHT_RATIO_MIN < bright_ratio < BRIGHT_RATIO_MAX:
        contours, _ = cv2.findContours(bright_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > CONTOUR_COUNT_THRESHOLD:
            return {
                'suspicious': True,
                'message': f"Multiple reflection-like patterns detected ({len(contours)} regions)",
                'vision_api_used': False
            }
    
    return {'suspicious': False, 'vision_api_used': HAS_VISION_API}

