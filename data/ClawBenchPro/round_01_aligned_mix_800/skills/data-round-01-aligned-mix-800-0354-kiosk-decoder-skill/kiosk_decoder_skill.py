import os
import json

def decode_kiosk_data(file_path: str) -> str:
    """
    Reads the proprietary binary dump from the kiosk and decrypts it into a JSON string.
    """
    if not os.path.exists(file_path):
        return json.dumps({"error": f"File not found: {file_path}"})
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            hex_data = f.read().strip()
            
        encrypted_text = bytes.fromhex(hex_data).decode('utf-8')
        
        # Internal decryption using the proprietary state key
        key = "GOVTECH2024"
        decrypted_text = "".join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(encrypted_text))
        
        # Verify it's valid JSON
        parsed = json.loads(decrypted_text)
        return json.dumps(parsed, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to decode kiosk data. Corrupted file or invalid format. Details: {str(e)}"})
