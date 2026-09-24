import os
import base64

def sec_log_decryptor(file_path: str) -> str:
    if not os.path.exists(file_path):
        return f"Error: File not found at '{file_path}'"
    
    try:
        with open(file_path, "rb") as f:
            encoded_content = f.read()
            
        decoded_bytes = base64.b64decode(encoded_content)
        return decoded_bytes.decode('utf-8')
    except Exception as e:
        return f"Decryption Error: The file appears to be corrupted or invalid format. Details: {str(e)}"
