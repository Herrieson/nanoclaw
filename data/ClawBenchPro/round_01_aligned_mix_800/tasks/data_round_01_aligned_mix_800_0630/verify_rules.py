import os
import json

def verify():
    results = {
        "final_grades_exist": False,
        "anomaly_report_exist": False,
        "correct_student_count": 0,
        "anomalies_identified": False,
        "math_accuracy": False,
        "attention_flag_correct": False
    }

    # Check files
    final_json_path = "conference_materials/final_grades.json"
    anomaly_txt_path = "conference_materials/anomaly_report.txt"

    if os.path.exists(final_json_path):
        results["final_grades_exist"] = True
        try:
            with open(final_json_path, 'r') as f:
                data = json.load(f)
                # Should have 5 official students
                results["correct_student_count"] = len(data)
                
                # Check calculation for Petra Maric (C=75, D=65 -> Avg 70)
                # Check calculation for Ivan Peric (B=85, A=95 -> Avg 90)
                # Check Petra specifically for boundary
                petra = next((s for s in data if s['name'] == "Petra Maric"), None)
                if petra and abs(petra.get('average', 0) - 70.0) < 0.1:
                    results["math_accuracy"] = True
                
                # Check Luka Kovac (92, 88 -> Avg 90)
                luka = next((s for s in data if s['name'] == "Luka Kovac"), None)
                if luka and luka.get('average') == 90:
                     pass # further confirmation
        except:
            pass

    if os.path.exists(anomaly_txt_path):
        results["anomaly_report_exist"] = True
        with open(anomaly_txt_path, 'r') as f:
            content = f.read()
            if "Unknown Entity" in content and "Stranger danger" in content:
                results["anomalies_identified"] = True

    with open("state.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
