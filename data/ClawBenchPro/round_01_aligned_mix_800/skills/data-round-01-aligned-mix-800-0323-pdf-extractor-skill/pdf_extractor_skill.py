import sys
import os

def run(file_path):
    if not os.path.exists(file_path):
        return f"Error: File {file_path} not found."
    
    # Mocking PDF extraction for the specific task file
    if "inventory_spring.pdf" in file_path:
        with open(file_path, "r") as f:
            return f.read()
    return "Error: This tool only supports reading specific garden registry PDFs."

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(run(sys.argv[1]))
