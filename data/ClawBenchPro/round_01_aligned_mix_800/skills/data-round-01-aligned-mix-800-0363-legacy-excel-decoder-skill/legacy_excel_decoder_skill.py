import sys
import os

def run(file_path):
    if not os.path.exists(file_path):
        return "Error: File not found."
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            if "INTERNAL_ENCODED_DATA:" in content:
                # Mock decoding logic
                decoded = content.replace("INTERNAL_ENCODED_DATA:", "").replace("|", "\n")
                return f"Decoding Successful:\n{decoded}"
            else:
                return "Error: Unsupported file format."
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python legacy_excel_decoder_skill.py <file_path>")
    else:
        print(run(sys.argv[1]))
