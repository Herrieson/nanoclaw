import os
import re
import json
import sys

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    file_path = os.path.join(workspace, "lumber_run.txt")
    result = {
        "file_exists": False,
        "2x4_correct": False,
        "4x4_correct": False
    }
    
    if os.path.exists(file_path):
        result["file_exists"] = True
        with open(file_path, "r") as f:
            content = f.read().lower()
        
        # 正确的 2x4 总长度为 77 feet
        if re.search(r"2x4.*77", content):
            result["2x4_correct"] = True
            
        # 正确的 4x4 总长度为 18 feet
        if re.search(r"4x4.*18", content):
            result["4x4_correct"] = True

    out_path = os.path.join(workspace, "verify_result.json")
    with open(out_path, "w") as f:
        json.dump(result, f)

if __name__ == "__main__":
    verify()
