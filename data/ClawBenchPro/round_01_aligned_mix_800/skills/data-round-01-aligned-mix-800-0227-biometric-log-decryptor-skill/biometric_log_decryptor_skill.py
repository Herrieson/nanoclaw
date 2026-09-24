import base64
import sys

def decrypt(file_path):
    try:
        with open(file_path, 'r') as f:
            data = f.read()
        return base64.b64decode(data).decode('utf-8')
    except Exception as e:
        return f"Decryption Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(decrypt(sys.argv[1]))
