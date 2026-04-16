import os
import json

def verify():
    report_path = "report.txt"
    result = {
        "report_exists": False,
        "content_correct": False,
        "formatting_correct": False,
        "details": ""
    }
    
    expected_lines = [
        "Architecture: 3",
        "Engineering: 3",
        "HR: 3",
        "Design: 2",
        "Maintenance: 1"
    ]
    
    if not os.path.exists(report_path):
        result["details"] = "report.txt not found."
        with open("verify_result.json", "w") as f:
            json.dump(result, f)
        return
        
    result["report_exists"] = True
    
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
            
        if lines == expected_lines:
            result["content_correct"] = True
            result["formatting_correct"] = True
            result["details"] = "Perfectly matched."
        else:
            result["details"] = f"Expected {expected_lines}, but got {lines}."
            
            # Check content irrespective of order
            if sorted(lines) == sorted(expected_lines):
                result["content_correct"] = True
                result["details"] = "Content correct but sorting or formatting might be off."
            
    except Exception as e:
        result["details"] = f"Error reading file: {str(e)}"
        
    with open("verify_result.json", "w") as f:
        json.dump(result, f)

if __name__ == "__main__":
    verify()
