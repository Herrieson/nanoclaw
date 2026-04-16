import os
import xml.etree.ElementTree as ET
import json

def verify():
    report_path = "final_grant_report.xml"
    results = {
        "file_exists": False,
        "valid_xml": False,
        "correct_families": [],
        "correct_totals": {},
        "logic_score": 0
    }

    if os.path.exists(report_path):
        results["file_exists"] = True
        try:
            tree = ET.parse(report_path)
            root = tree.getroot()
            results["valid_xml"] = True
            
            # 预期数据逻辑:
            # FAM-001: 300.50 (DB) + 250 (Log) = 550.50 (High) -> OK
            # FAM-002: 600 (Low) -> NO (Only High Priority)
            # FAM-003: 450 (DB) + 100 (Notes) = 550 (High) -> OK
            # FAM-004: 1200 (High) -> OK
            # FAM-005: 750 (Log, High) -> OK
            # FAM-006: 900 (Notes, High) -> OK

            expected = {
                "FAM-001": 550.5,
                "FAM-003": 550.0,
                "FAM-004": 1200.0,
                "FAM-005": 750.0,
                "FAM-006": 900.0
            }

            found_families = {}
            for family in root.findall('family'):
                fid = family.find('id').text
                total = float(family.find('total').text)
                found_families[fid] = total
            
            results["correct_families"] = list(found_families.keys())
            
            matches = 0
            for fid, total in expected.items():
                if fid in found_families and abs(found_families[fid] - total) < 0.01:
                    matches += 1
            
            results["logic_score"] = (matches / len(expected)) * 100

        except Exception as e:
            results["error"] = str(e)

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
