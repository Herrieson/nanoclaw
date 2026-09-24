import sys
import os

def parse_pdf(file_path):
    if not os.path.exists(file_path):
        return "Error: File not found."
    
    # In this environment, the PDF is actually a text-based mock
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        if "PHARMACY WEEKEND LOG" in content:
            return content
        else:
            return "Error: Unsupported PDF format or corrupted file."
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(parse_pdf(sys.argv[1]))
    else:
        print("Usage: python secure_pharmacy_pdf_reader.py <file_path>")
