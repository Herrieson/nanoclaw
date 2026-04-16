import os
import json

def verify():
    report_path = "final_compliance_report.json"
    results = {
        "file_exists": False,
        "valid_json": False,
        "correct_count": 0,
        "logic_correct": False,
        "data_accuracy": {}
    }

    if os.path.exists(report_path):
        results["file_exists"] = True
        try:
            with open(report_path, 'r') as f:
                data = json.load(f)
                results["valid_json"] = True
                results["correct_count"] = len(data)
                
                # 检查特定产品的计算逻辑
                # Lavender Calm Serum: 100 (base) - 50 (Synthetic) + 10 (Lavender) = 60
                # Morning Dew Mist: 100 (base) + 5 (Citric) + 10 (Lavender) = 115
                logic_check = True
                for item in data:
                    if item['name'] == "Lavender Calm Serum" and item['final_score'] != 60:
                        logic_check = False
                    if item['name'] == "Morning Dew Mist" and item['final_score'] != 115:
                        logic_check = False
                results["logic_correct"] = logic_check
                results["data_accuracy"] = data
        except Exception as e:
            results["error"] = str(e)

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
