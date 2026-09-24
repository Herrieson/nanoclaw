import sys
import os
import base64
import json

def parse_ezpos(filepath):
    if not os.path.exists(filepath):
        return f"Error: File '{filepath}' not found."
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            
        if "PAYLOAD:" not in content:
            return "Error: Invalid EZPOS format. Missing payload header."
            
        # Extract the base64 payload
        payload = content.split("PAYLOAD:")[1].split("\n")[0].strip()
        
        # Decode the payload
        decoded_bytes = base64.b64decode(payload)
        decoded_str = decoded_bytes.decode('utf-8')
        
        # Verify it's valid JSON
        json_data = json.loads(decoded_str)
        return json.dumps(json_data, indent=4)
        
    except Exception as e:
        return f"Decryption Error: Could not parse file. {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        print(parse_ezpos(file_path))
    else:
        print("Usage: python pos_receipt_parser.py <filepath.ezpos>")
