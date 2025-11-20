import numpy as np
from scipy.io import wavfile
from scipy import signal
import subprocess
import os

try:
    import librosa
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False
    print("Warning: librosa not available. Using fallback audio analysis.")

def check_reverb(video_path):
    """Simplified reverb detection using audio analysis"""
    
    # Extract audio using ffmpeg
    audio_path = os.path.join(os.path.dirname(video_path), 'temp_audio.wav')
    
    try:
        # Extract audio track
        subprocess.run([
            'ffmpeg', '-i', video_path, '-ab', '160k', 
            '-ac', '2', '-ar', '44100', '-vn', audio_path, '-y'
        ], capture_output=True, check=True)
    except subprocess.CalledProcessError as e:
        return {
            'score': 50,
            'findings': ['Could not extract audio from video'],
            'reverb_coefficient': 0
        }
    except FileNotFoundError:
        return {
            'score': 50,
            'findings': ['ffmpeg not found. Please install ffmpeg.'],
            'reverb_coefficient': 0
        }
    
    # Load and analyze audio
    findings = []
    score = 100
    
    try:
        if HAS_LIBROSA:
            # Use librosa for better audio analysis
            y, sr = librosa.load(audio_path, sr=22050)
            
            # Calculate spectral rolloff (reverb indicator)
            rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, roll_percent=0.85)
            rolloff_mean = np.mean(rolloff)
            
            # Analyze reverb patterns
            if rolloff_mean < 2000:  # Too dead/studio-like
                findings.append("Unusual acoustic dampening detected")
                score -= 30
            elif rolloff_mean > 8000:  # Too much reverb
                findings.append("Reverb pattern inconsistent with visible space")
                score -= 40
            
            # Check for complete silence periods (common in bad fakes)
            silence_threshold = 0.01
            silence_ratio = np.sum(np.abs(y) < silence_threshold) / len(y)
            if silence_ratio > 0.3:
                findings.append("Unnatural silence patterns detected")
                score -= 25
            
            reverb_coeff = float(rolloff_mean)
        else:
            # Fallback: basic audio analysis without librosa
            try:
                sample_rate, y = wavfile.read(audio_path)
                if len(y.shape) > 1:
                    y = y[:, 0]  # Use first channel if stereo
                
                # Simple amplitude analysis
                mean_amplitude = np.mean(np.abs(y))
                std_amplitude = np.std(np.abs(y))
                
                # Check for unusual patterns
                if mean_amplitude < 100:  # Very quiet
                    findings.append("Unusually quiet audio detected")
                    score -= 20
                
                if std_amplitude < 50:  # Very flat audio
                    findings.append("Unnatural audio flatness detected")
                    score -= 25
                
                reverb_coeff = float(mean_amplitude)
            except Exception as e:
                findings.append(f"Audio analysis error: {str(e)}")
                score = 75
                reverb_coeff = 0
        
    except Exception as e:
        findings.append(f"Error analyzing audio: {str(e)}")
        score = 75
        reverb_coeff = 0
    
    finally:
        # Clean up temp audio file
        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
        except:
            pass
    
    return {
        'score': max(0, score),
        'findings': findings if findings else ["Audio acoustics appear normal"],
        'reverb_coefficient': reverb_coeff
    }

