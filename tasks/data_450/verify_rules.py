import os
import json
import re

def verify():
    base_dir = "."
    summary_file = os.path.join(base_dir, 'eco_summary.txt')
    
    result = {
        "summary_file_exists": False,
        "energy_correct": False,
        "bin_correct": False,
        "extracted_text": ""
    }
    
    if os.path.exists(summary_file):
        result["summary_file_exists"] = True
        with open(summary_file, 'r', encoding='utf-8') as f:
            content = f.read()
            result["extracted_text"] = content
            
            # Check for total energy (345.6)
            if re.search(r'345\.6', content):
                result["energy_correct"] = True
                
            # Check for worst bin (BIN-004)
            if re.search(r'BIN-004', content, re.IGNORECASE):
                result["bin_correct"] = True

    # Output the result for the LLM judge
    result_path = os.path.join(base_dir, 'verify_result.json')
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)

if __name__ == '__main__':
    verify()
