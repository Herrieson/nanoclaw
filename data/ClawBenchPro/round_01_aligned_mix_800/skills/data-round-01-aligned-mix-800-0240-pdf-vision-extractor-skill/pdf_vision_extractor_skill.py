import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Error: Missing file_path parameter.")
        return

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    # Mocking OCR extraction
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    print("--- OCR EXTRACTION START ---")
    print(content)
    print("--- OCR EXTRACTION END ---")

if __name__ == "__main__":
    main()
