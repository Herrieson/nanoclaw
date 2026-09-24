import sys
import base64
import os

def run(file_path):
    if not os.path.exists(file_path):
        return f"Error: File {file_path} not found."
    
    try:
        with open(file_path, "r") as f:
            encoded = f.read()
        decoded = base64.b64decode(encoded).decode()
        return decoded
    except Exception as e:
        return f"Error processing file: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(run(sys.argv[1]))
