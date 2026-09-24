import sys
import base64
import os

def decode_medlog(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' does not exist.")
        sys.exit(1)
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            encoded_content = f.read()
            
        decoded_bytes = base64.b64decode(encoded_content)
        decoded_text = decoded_bytes.decode('utf-8')
        
        print("=== DECODED MEDLOG CONTENT ===")
        print(decoded_text)
        print("==============================")
    except Exception as e:
        print(f"Error decoding file: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python medlog_decoder.py <filepath>")
        sys.exit(1)
        
    decode_medlog(sys.argv[1])
