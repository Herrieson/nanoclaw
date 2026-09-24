import os
import base64

def parse_iwl_file(file_path: str) -> str:
    if not os.path.exists(file_path):
        return f"Error: File '{file_path}' does not exist."
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        if len(lines) < 2 or "SMARTWEAVE_IWL_MAGIC_HEADER" not in lines[0]:
            return "Error: Invalid .iwl file format or missing magic header."
            
        encoded_payload = lines[1].strip()
        decoded_bytes = base64.b64decode(encoded_payload)
        decoded_str = decoded_bytes.decode('utf-8')
        
        return f"[DECODED TELEMETRY]: {decoded_str}"
        
    except Exception as e:
        return f"System Error: Failed to parse .iwl file. Details: {str(e)}"
