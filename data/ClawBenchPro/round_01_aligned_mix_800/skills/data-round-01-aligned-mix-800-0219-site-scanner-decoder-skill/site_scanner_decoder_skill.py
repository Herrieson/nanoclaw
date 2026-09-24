import sys
import os
import base64

def decode_bdat(file_path):
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"
    
    try:
        with open(file_path, "rb") as f:
            content = f.read()
            
        header_marker = b"MARCUS_SCANNER_V1\n"
        if not content.startswith(header_marker):
            return "Error: Invalid file format. Missing proprietary header."
            
        payload = content[len(header_marker):]
        decoded_text = base64.b64decode(payload).decode("utf-8")
        return decoded_text
    except Exception as e:
        return f"Decoder Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python site_scanner_decoder_skill.py <file_path>")
        sys.exit(1)
    
    result = decode_bdat(sys.argv[1])
    print(result)
