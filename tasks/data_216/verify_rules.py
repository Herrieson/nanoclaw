import os
import json

def verify():
    results = {
        "mfr_exists": False,
        "correct_officer_found": False,
        "format_adherence": False,
        "content_accuracy": False
    }
    
    report_path = "contact_briefing.txt"
    if os.path.exists(report_path):
        results["mfr_exists"] = True
        with open(report_path, "r") as f:
            content = f.read()
            
            # 检查关键信息
            if "Arthur Miller" in content and "850-555-0199" in content:
                results["correct_officer_found"] = True
            
            # 检查军事格式
            if "MEMORANDUM FOR RECORD" in content and "SUBJECT:" in content:
                results["format_adherence"] = True
                
            if "Tallahassee, FL" in content:
                results["content_accuracy"] = True

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
