import os
import json
import csv

def verify():
    target_file = "final_art_catalog.csv"
    state = {
        "file_exists": False,
        "correct_headers": False,
        "rows_count": 0,
        "correct_data": False,
        "correct_sort": False,
        "extracted_rows": []
    }

    if os.path.exists(target_file):
        state["file_exists"] = True
        try:
            with open(target_file, "r") as f:
                reader = csv.reader(f)
                headers = next(reader, [])
                if [h.strip() for h in headers] == ["part_id", "motif", "cost"]:
                    state["correct_headers"] = True
                
                rows = []
                for row in reader:
                    if len(row) == 3:
                        rows.append({
                            "part_id": row[0].strip(),
                            "motif": row[1].strip().lower(),
                            "cost": float(row[2].strip())
                        })
                
                state["rows_count"] = len(rows)
                state["extracted_rows"] = rows

                # Expected rows (ignoring case of motif for comparison, and handling float tolerance)
                # BP-003: 68.0, BP-002: 33.5, BP-001: 12.5, BP-004: 10.0
                expected_data = {
                    "BP-003": ("wave", 68.0),
                    "BP-002": ("leaf", 33.5),
                    "BP-001": ("wave", 12.5),
                    "BP-004": ("leaf", 10.0)
                }

                parsed_data = {r["part_id"]: (r["motif"], r["cost"]) for r in rows}

                # Check exact data match
                data_correct = True
                if len(parsed_data) != 4:
                    data_correct = False
                else:
                    for pid, (emotif, ecost) in expected_data.items():
                        if pid not in parsed_data:
                            data_correct = False
                            break
                        pmotif, pcost = parsed_data[pid]
                        if pmotif != emotif or abs(pcost - ecost) > 0.01:
                            data_correct = False
                            break
                state["correct_data"] = data_correct

                # Check sorting (descending by cost)
                if len(rows) == 4:
                    costs = [r["cost"] for r in rows]
                    if costs == sorted(costs, reverse=True):
                        state["correct_sort"] = True

        except Exception as e:
            state["error"] = str(e)

    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
