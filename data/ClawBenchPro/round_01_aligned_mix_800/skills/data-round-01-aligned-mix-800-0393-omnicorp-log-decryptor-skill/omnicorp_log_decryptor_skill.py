import base64
import os

def execute(file_path: str) -> str:
    if not os.path.exists(file_path):
        return f"Error: File '{file_path}' not found."
    
    try:
        with open(file_path, "rb") as f:
            encrypted_bytes = f.read()
            
        # Reverse OmniCorp proprietary obfuscation: Base64 decode, then reverse string
        reversed_text = base64.b64decode(encrypted_bytes).decode('utf-8')
        plaintext = reversed_text[::-1]
        
        return plaintext
    except Exception as e:
        return f"Decryption Error: {str(e)}. Ensure the file is a valid OmniCorp .enc format."
