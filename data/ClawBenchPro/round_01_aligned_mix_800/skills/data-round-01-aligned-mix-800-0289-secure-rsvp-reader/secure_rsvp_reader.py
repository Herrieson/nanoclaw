import sys
import os
import base64

def decode_file(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        sys.exit(1)
        
    try:
        with open(file_path, "r") as f:
            encoded_content = f.read().strip()
        
        decoded_bytes = base64.b64decode(encoded_content)
        decoded_str = decoded_bytes.decode('utf-8')
        print(decoded_str)
    except Exception as e:
        print(f"Error decoding file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python secure_rsvp_reader.py <file_path>")
        sys.exit(1)
        
    decode_file(sys.argv[1])
