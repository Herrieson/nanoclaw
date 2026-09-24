import sys
import os

def run(file_path):
    if not os.path.exists(file_path):
        return "Error: File not found."
    with open(file_path, 'r') as f:
        return f.read()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(run(sys.argv[1]))
