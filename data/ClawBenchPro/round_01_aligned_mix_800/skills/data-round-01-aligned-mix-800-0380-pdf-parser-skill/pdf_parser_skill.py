import sys
import os

def extract_text(file_path):
    if not os.path.exists(file_path):
        return "Error: File not found."
    if not file_path.endswith(".pdf"):
        return "Error: Not a PDF file."
    
    # Simulating PDF extraction
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf_parser_skill.py <file_path>")
    else:
        print(extract_text(sys.argv[1]))
