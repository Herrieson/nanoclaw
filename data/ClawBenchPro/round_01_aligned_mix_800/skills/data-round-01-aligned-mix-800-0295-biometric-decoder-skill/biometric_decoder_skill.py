import sys
import base64
import os

def decode_file(file_path):
    if not os.path.exists(file_path):
        return "Error: Biometric file not found."
    try:
        with open(file_path, "rb") as f:
            encoded_data = f.read()
        # Decode the proprietary format (simulated with Base64)
        decoded_bytes = base64.b64decode(encoded_data)
        return decoded_bytes.decode('utf-8')
    except Exception as e:
        return f"Decoder Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python biometric_decoder_skill.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    result = decode_file(file_path)
    print(result)
