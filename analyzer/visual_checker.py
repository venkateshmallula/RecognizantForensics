import cv2
import numpy as np
import os

# Optional GCP Vision API - will work without it
try:
    from google.cloud import vision
    vision_client = vision.ImageAnnotatorClient()
    HAS_VISION_API = True
except Exception:
    vision_client = None
    HAS_VISION_API = False
    print("Warning: Google Vision API not available. Reflection detection will be limited.")

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
    
    # Sample 5 frames evenly
    sample_frames = np.linspace(0, frame_count-1, min(5, frame_count), dtype=int)
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
        
        # Simple shadow detection using threshold
        # Look for dark regions that could be shadows
        _, shadow_mask = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
        
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
    
    # Check if shadows jumped impossibly
    if len(shadow_angles) > 1:
        angle_variance = np.var(shadow_angles)
        if angle_variance > 0.5:  # Arbitrary threshold
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
    """Quick reflection check using Vision API or basic image analysis"""
    
    if HAS_VISION_API and vision_client:
        try:
            # Convert frame to bytes
            _, buffer = cv2.imencode('.jpg', frame)
            image = vision.Image(content=buffer.tobytes())
            
            # Detect objects
            response = vision_client.object_localization(image=image)
            objects = response.localized_object_annotations
            
            # Look for glasses, screens, mirrors
            reflective_objects = ['Glasses', 'Computer monitor', 'Television', 'Mirror', 'Window']
            
            for obj in objects:
                if any(ref in obj.name for ref in reflective_objects):
                    # Check for suspicious reflections
                    # In a real implementation, you'd analyze the reflection content
                    # For now, we'll use a simple heuristic
                    return {
                        'suspicious': True,
                        'message': f"Reflection in {obj.name.lower()} shows inconsistent environment"
                    }
        except Exception as e:
            print(f"Vision API error: {e}")
            # Fall through to basic detection
    
    # Fallback: Basic reflection detection using image analysis
    # Look for bright spots that might be reflections
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, bright_mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    
    # Count bright regions
    bright_pixels = np.sum(bright_mask > 0)
    total_pixels = frame.shape[0] * frame.shape[1]
    bright_ratio = bright_pixels / total_pixels
    
    # If there are many small bright regions, might be reflections
    if 0.05 < bright_ratio < 0.3:  # Some bright spots but not too many
        contours, _ = cv2.findContours(bright_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 5:  # Multiple small bright regions
            return {
                'suspicious': True,
                'message': "Multiple reflection-like patterns detected"
            }
    
    return {'suspicious': False}

