import sys
import os

def run(file_path):
    if not os.path.exists(file_path):
        return "Error: File not found."
    
    try:
        with open(file_path, "rb") as f:
            content = f.read().decode('utf-8')
            if not content.startswith("AURA_PALETTE"):
                return "Error: Invalid palette format for Project Aura."
            
            parts = content.split(":")
            # Format: HEADER:PRIMARY:SECONDARY:TEXT
            return {
                "primary_color": parts[1],
                "secondary_color": parts[2],
                "text_color": parts[3]
            }
    except Exception as e:
        return f"Error parsing palette: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(run(sys.argv[1]))
