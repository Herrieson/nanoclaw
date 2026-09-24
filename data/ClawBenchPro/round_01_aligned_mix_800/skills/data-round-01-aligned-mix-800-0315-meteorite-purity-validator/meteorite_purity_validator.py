import json

def validate_and_calibrate(artifact_id, raw_density):
    """
    Applies Dr. Liang's proprietary calibration curve: 
    Calibrated = Raw * 1.1 (Simulation of impurity correction)
    """
    if not artifact_id or not isinstance(raw_density, (int, float)):
        return json.dumps({"error": "Invalid input parameters."})
    
    calibrated = round(float(raw_density) * 1.1, 2)
    return json.dumps({
        "artifact_id": artifact_id,
        "status": "Authenticated",
        "calibrated_density": calibrated
    })
