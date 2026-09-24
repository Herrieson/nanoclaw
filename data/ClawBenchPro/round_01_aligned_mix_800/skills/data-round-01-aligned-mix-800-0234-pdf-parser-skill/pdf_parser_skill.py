import sys
import os

def parse_pdf(path):
    if not os.path.exists(path):
        return "Error: File not found."
    with open(path, 'r') as f:
        content = f.read()
    return content.replace("[SECURE DOCUMENT]", "EXTRACTED CONTENT:")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(parse_pdf(sys.argv[1]))
