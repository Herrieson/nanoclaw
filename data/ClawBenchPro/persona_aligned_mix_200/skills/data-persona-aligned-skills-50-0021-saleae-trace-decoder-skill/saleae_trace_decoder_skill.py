import base64
import os

def decode_trace(file_path: str) -> str:
    if not os.path.exists(file_path):
        return f"Error: File '{file_path}' does not exist."
    
    if not file_path.endswith('.sal'):
        return "Error: Invalid file format. Only .sal files are supported."

    try:
        with open(file_path, "rb") as f:
            encoded_data = f.read()
        # Decode the dummy proprietary format
        decoded_text = base64.b64decode(encoded_data).decode('utf-8')
        return decoded_text
    except Exception as e:
        return f"Decoder Error: Failed to parse trace file. {str(e)}"
