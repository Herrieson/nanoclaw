import sys
import os

def run(file_path):
    if not os.path.exists(file_path):
        return "Error: File not found."
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

if __name__ == "__main__":
    print(run(sys.argv[1] if len(sys.argv) > 1 else ""))
