import sys
import json
import base64

def parse_bin(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
            decoded = base64.b64encode(base64.b64decode(data)).decode('utf-8') # Just a check
            # Real logic
            original = base64.b64decode(data).decode('utf-8')
            return original
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python bin_concept_parser_skill.py <path>")
    else:
        print(parse_bin(sys.argv[1]))
