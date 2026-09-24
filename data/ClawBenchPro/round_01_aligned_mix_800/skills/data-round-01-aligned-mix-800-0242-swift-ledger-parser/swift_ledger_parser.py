import sys
import base64
import json
import os

def parse_ledger(path):
    if not os.path.exists(path):
        return "Error: File not found."
    try:
        with open(path, "r") as f:
            lines = f.readlines()
            # Extract content between markers
            content = "".join([l for l in lines if "---" not in l]).strip()
            decoded = base64.b64encode(base64.b64decode(content)).decode() # Validate b64
            data = base64.b64decode(content).decode()
            return data # This is the JSON string
    except Exception as e:
        return f"Error: Decryption failed. {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(parse_ledger(sys.argv[1]))
