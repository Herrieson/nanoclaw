import math

def spacecraft_quaternion_normalizer(q_w: float, q_x: float, q_y: float, q_z: float) -> dict:
    """
    Normalizes a given quaternion to ensure its length is 1.0.
    Simulates a flight-certified safety validation tool.
    """
    try:
        # Calculate magnitude
        magnitude = math.sqrt(q_w**2 + q_x**2 + q_y**2 + q_z**2)
        
        if magnitude == 0:
            return {"error": "Zero magnitude quaternion cannot be normalized."}
            
        # Normalize
        norm_w = q_w / magnitude
        norm_x = q_x / magnitude
        norm_y = q_y / magnitude
        norm_z = q_z / magnitude
        
        return {
            "q_w": round(norm_w, 6),
            "q_x": round(norm_x, 6),
            "q_y": round(norm_y, 6),
            "q_z": round(norm_z, 6)
        }
    except Exception as e:
        return {"error": f"Normalization failed: {str(e)}"}
