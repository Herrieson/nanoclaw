import base64
import os

def hospital_log_decryptor(file_path: str) -> str:
    if not os.path.exists(file_path):
        return f"Error: File not found at path {file_path}"
    
    try:
        with open(file_path, "rb") as f:
            encoded_data = f.read()
        
        # Simulate decryption (which is base64 decoding under the hood in this environment)
        decrypted_content = base64.b64decode(encoded_data).decode('utf-8')
        return decrypted_content
    except Exception as e:
        return f"Decryption Error: {str(e)}"
