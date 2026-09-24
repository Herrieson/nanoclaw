import os
import base64
import json

def decode_bci_markers(filepath: str) -> str:
    """
    Decodes the proprietary V2 BCI marker file and returns a JSON string.
    """
    if not os.path.exists(filepath):
        return json.dumps({"error": f"File not found: {filepath}"})
    
    try:
        with open(filepath, "rb") as f:
            data = f.read()
        
        # Check header
        if not data.startswith(b"BCI_MRK_V2\x00\xFF\xAA"):
            return json.dumps({"error": "Invalid file format. Missing BCI_MRK_V2 header."})
        
        # Extract payload
        payload = data[13:]
        decoded_text = base64.b64decode(payload).decode('utf-8')
        
        events = []
        for line in decoded_text.strip().split('\n'):
            if not line: continue
            parts = line.split('~')
            if len(parts) == 3:
                events.append({
                    "stim_id": parts[0],
                    "timestamp_ms": int(parts[1]),
                    "target_type": parts[2]
                })
        
        return json.dumps(events, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to parse markers: {str(e)}"})
