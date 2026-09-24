import sys
import os
import json

def analyze_spectrum(file_path):
    # Mocking analysis results based on filename to ensure consistency with verify_rules
    filename = os.path.basename(file_path).lower()
    if "b105" in filename:
        return json.dumps({"red_pigment_pct": 16, "status": "Success"})
    elif "b106" in filename:
        return json.dumps({"red_pigment_pct": 12, "status": "Success"})
    elif "b104" in filename:
        return json.dumps({"red_pigment_pct": 2, "status": "Success"})
    else:
        return json.dumps({"error": "File format unrecognized or noise level too high."})

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python spectro_color_analyzer_skill.py <file_path>")
    else:
        print(analyze_spectrum(sys.argv[1]))
