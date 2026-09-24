import base64
import sys
import os

def run(file_path):
    if not os.path.exists(file_path):
        return "Error: File not found."
    
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            # Extract content between markers
            content = "".join([l.strip() for l in lines if "---" not in l])
            decoded = base64.b64decode(content).decode('utf-8')
            return f"Decoded Content:\n{decoded}"
    except Exception as e:
        return f"Error decoding QR: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(run(sys.argv[1]))
