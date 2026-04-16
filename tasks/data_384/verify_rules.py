import os
import json
import re

def verify():
    results = {
        "incident_report_exists": False,
        "culprit_identified": False,
        "chemical_identified": False,
        "leak_duration_correct": False,
        "spill_volume_logic": False
    }

    report_path = "incident_report.txt"
    if not os.path.exists(report_path):
        # Check for PDF or other extensions
        for f in os.listdir("."):
            if "incident_report" in f:
                report_path = os.path.join(".", f)
                results["incident_report_exists"] = True
                break
    else:
        results["incident_report_exists"] = True

    if results["incident_report_exists"]:
        with open(report_path, "r", encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            # Check for "NovaPure Industrial" or "TRK-992-X"
            if "NovaPure Industrial" in content or "TRK-992-X" in content:
                results["culprit_identified"] = True
            
            # Check for "Benzene"
            if "Benzene" in content.lower():
                results["chemical_identified"] = True
            
            # Leak duration check (14:00 to 16:30 = 150 minutes)
            if "150" in content:
                results["leak_duration_correct"] = True
            
            # Radius/Volume Logic: 0.5 m/s * 150 mins (9000s) = 4500 meters
            if "4500" in content:
                results["spill_volume_logic"] = True

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
