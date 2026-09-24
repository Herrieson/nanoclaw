import sys
import os
import base64

def main():
    if len(sys.argv) < 2:
        print("Error: Missing file_path parameter.")
        sys.exit(1)
        
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        sys.exit(1)
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            encoded_content = f.read().strip()
            decoded_bytes = base64.b64decode(encoded_content)
            print(decoded_bytes.decode('utf-8'))
    except Exception as e:
        print(f"Decoder Error: Could not decode {file_path}. Is it a valid .shiftlog file? Details: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
