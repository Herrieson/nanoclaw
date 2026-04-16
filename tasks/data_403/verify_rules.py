import os
import json
import csv

def verify():
    workspace = "workspace"
    records_dir = os.path.join(workspace, "vintage_records")
    csv_file = os.path.join(workspace, "sell_list.csv")
    
    state = {
        "csv_exists": False,
        "csv_has_header": False,
        "csv_correct_records": False,
        "csv_row_count": 0,
        "files_renamed_correctly": False,
        "json_content_valid": False,
        "unexpected_files": []
    }

    expected_sell_list = [
        ("Miles Davis", "Kind of Blue", "1959", "50"),
        ("Marvin Gaye", "What's Going On", "1971", "40"),
        ("John Coltrane", "A Love Supreme", "1965", "60"),
        ("Aretha Franklin", "Lady Soul", "1968", "45"),
        ("Thelonious Monk", "Brilliant Corners", "1957", "70"),
        ("Curtis Mayfield", "Superfly", "1972", "38"),
        ("Herbie Hancock", "Head Hunters", "1973", "42")
    ]

    # 1. Check CSV
    if os.path.exists(csv_file):
        state["csv_exists"] = True
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
                
                if len(rows) > 0:
                    header = [h.strip() for h in rows[0]]
                    if header == ["Artist", "Album", "Year", "Price"]:
                        state["csv_has_header"] = True
                    
                    data_rows = rows[1:]
                    state["csv_row_count"] = len(data_rows)
                    
                    # Check if all expected records are in the CSV
                    extracted_records = set()
                    for r in data_rows:
                        if len(r) == 4:
                            extracted_records.add((r[0].strip(), r[1].strip(), r[2].strip(), r[3].strip()))
                    
                    expected_set = set(expected_sell_list)
                    if expected_set == extracted_records:
                        state["csv_correct_records"] = True
        except Exception:
            pass

    # 2. Check Renamed Files & Content
    expected_filenames = [
        "Miles Davis - Kind of Blue.json",
        "Marvin Gaye - What's Going On.json",
        "Michael Jackson - Thriller.json",
        "John Coltrane - A Love Supreme.json",
        "Aretha Franklin - Lady Soul.json",
        "Pink Floyd - Dark Side of the Moon.json",
        "Stevie Wonder - Songs in the Key of Life.json",
        "Thelonious Monk - Brilliant Corners.json",
        "Curtis Mayfield - Superfly.json",
        "Herbie Hancock - Head Hunters.json",
        "Nina Simone - Baltimore.json"
    ]

    if os.path.exists(records_dir):
        files = os.listdir(records_dir)
        json_files = [f for f in files if f.endswith('.json')]
        
        # Check if expected files exist
        all_expected_exist = all(f in json_files for f in expected_filenames)
        state["files_renamed_correctly"] = all_expected_exist
        
        # Check for garbage files
        state["unexpected_files"] = [f for f in files if f not in expected_filenames]

        # Check content validity for a sample
        if all_expected_exist:
            try:
                sample_file = os.path.join(records_dir, "Miles Davis - Kind of Blue.json")
                with open(sample_file, 'r') as f:
                    data = json.load(f)
                    if data.get("artist") == "Miles Davis" and data.get("genre") == "Jazz":
                        state["json_content_valid"] = True
            except Exception:
                pass

    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
