import os
import re
import json

def verify():
    report_path = "summary_report.md"
    state = {
        "report_exists": False,
        "table_found": False,
        "headers_correct": False,
        "data_accuracy": {}
    }

    if not os.path.exists(report_path):
        print(json.dumps(state))
        return

    state["report_exists"] = True

    expected_data = {
        "Blue Jay": {"count": 4, "students": ["Bob", "David", "Emma"]},
        "Monarch Butterfly": {"count": 2, "students": ["Alice", "Liam"]},
        "Red Maple": {"count": 4, "students": ["Alice", "Charlie", "David", "Noah"]},
        "White Oak": {"count": 2, "students": ["Emma", "Liam"]}
    }

    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract markdown table rows
    table_rows = re.findall(r'\|(.+?)\|(.+?)\|(.+?)\|', content)
    
    if len(table_rows) > 1:
        state["table_found"] = True
        
        # Check headers
        headers = [col.strip().lower() for col in table_rows[0]]
        if "species" in headers[0] and "count" in headers[1] and "students" in headers[2]:
            state["headers_correct"] = True

        # Parse data rows
        parsed_data = {}
        for row in table_rows[1:]:
            # Skip separator row e.g. |---|---|---|
            if '---' in row[0]:
                continue
            
            species = row[0].strip()
            try:
                count = int(row[1].strip())
            except ValueError:
                continue
                
            students_raw = row[2].strip()
            students = [s.strip() for s in students_raw.split(",")]
            students.sort()
            
            parsed_data[species] = {
                "count": count,
                "students": students
            }

        # Compare with expected
        match_stats = {}
        for species, exp in expected_data.items():
            if species in parsed_data:
                act = parsed_data[species]
                count_match = act["count"] == exp["count"]
                students_match = act["students"] == exp["students"]
                match_stats[species] = {
                    "found": True,
                    "count_match": count_match,
                    "students_match": students_match,
                    "actual_count": act["count"],
                    "actual_students": act["students"]
                }
            else:
                match_stats[species] = {"found": False}
        
        state["data_accuracy"] = match_stats

    print(json.dumps(state))

if __name__ == "__main__":
    verify()
