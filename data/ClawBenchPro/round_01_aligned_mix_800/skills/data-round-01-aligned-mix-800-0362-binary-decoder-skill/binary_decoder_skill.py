import sys
import base64

def run(file_path):
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
            return base64.b64decode(data).decode('utf-8')
    except Exception as e:
        return f"Error decoding binary: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(run(sys.argv[1]))
