def calculate_confidence(audio_results, visual_results):
    """Combine scores into final verdict"""
    
    # Weighted average (audio is harder to fake well)
    audio_weight = 0.6
    visual_weight = 0.4
    
    combined_score = (
        audio_results['score'] * audio_weight + 
        visual_results['score'] * visual_weight
    )
    
    # Generate verdict
    if combined_score >= 80:
        verdict = "LIKELY AUTHENTIC"
        confidence = "High confidence"
    elif combined_score >= 50:
        verdict = "SUSPICIOUS"
        confidence = "Medium confidence"
    else:
        verdict = "LIKELY DEEPFAKE"
        confidence = "High confidence"
    
    # Combine all findings
    all_findings = audio_results['findings'] + visual_results['findings']
    
    return {
        'score': round(combined_score, 2),
        'verdict': verdict,
        'confidence': confidence,
        'key_indicators': all_findings[:3] if all_findings else ["No anomalies detected"],  # Top 3 for demo
        'technical_details': {
            'audio_reverb': audio_results.get('reverb_coefficient', 0),
            'shadow_variance': visual_results.get('shadow_variance', 0)
        }
    }

