import sys
import os

def parse_rfu(file_path):
    if not os.path.exists(file_path):
        return f"Error: File {file_path} not found."
    
    results = []
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith("HDR"): continue
                if "|" in line:
                    sid, val = line.strip().split("|")
                    results.append({"sample_id": sid, "rfu_value": float(val)})
        return results
    except Exception as e:
        return f"Error parsing proprietary format: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fluorescence_qc_analyzer_skill.py <file_path>")
    else:
        print(parse_rfu(sys.argv[1]))
