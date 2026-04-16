import os
import json
import csv
import re

def verify():
    base_dir = "."
    cleaned_dir = os.path.join(base_dir, "cleaned_texts")
    csv_file = os.path.join(base_dir, "theme_analysis.csv")
    
    result = {
        "cleaned_dir_exists": False,
        "all_files_cleaned": False,
        "csv_exists": False,
        "csv_format_correct": False,
        "csv_data_correct": False,
        "details": []
    }

    # 1. Check Cleaned Directory
    if os.path.exists(cleaned_dir) and os.path.isdir(cleaned_dir):
        result["cleaned_dir_exists"] = True
        cleaned_files = os.listdir(cleaned_dir)
        if len(cleaned_files) == 3:
            typos_fixed = True
            for f in cleaned_files:
                filepath = os.path.join(cleaned_dir, f)
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                    if re.search(r'\bteh\b', content) or re.search(r'\bwhcih\b', content):
                        typos_fixed = False
                        result["details"].append(f"Typos found in {f}")
            result["all_files_cleaned"] = typos_fixed
        else:
            result["details"].append(f"Expected 3 cleaned files, found {len(cleaned_files)}")
    else:
        result["details"].append("Cleaned directory does not exist.")

    # 2. Check CSV
    expected_data = {
        "The Iron Mill": {"Author": "John Smith", "Nature_Count": "1", "Industry_Count": "3"},
        "Whispers of the Forest": {"Author": "Jane Doe", "Nature_Count": "5", "Industry_Count": "0"},
        "Progress and Ruin": {"Author": "Arthur Pendelton", "Nature_Count": "2", "Industry_Count": "3"}
    }

    if os.path.exists(csv_file):
        result["csv_exists"] = True
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                if headers == ['Title', 'Author', 'Nature_Count', 'Industry_Count']:
                    result["csv_format_correct"] = True
                    
                    data_correct = True
                    rows = list(reader)
                    if len(rows) != 3:
                        data_correct = False
                        result["details"].append("CSV does not have 3 data rows.")
                    
                    for row in rows:
                        title = row.get("Title", "")
                        if title in expected_data:
                            exp = expected_data[title]
                            if row["Author"] != exp["Author"] or \
                               str(row["Nature_Count"]) != exp["Nature_Count"] or \
                               str(row["Industry_Count"]) != exp["Industry_Count"]:
                                data_correct = False
                                result["details"].append(f"Incorrect data for {title}: {row}")
                        else:
                            data_correct = False
                            result["details"].append(f"Unexpected title in CSV: {title}")
                            
                    result["csv_data_correct"] = data_correct
                else:
                    result["details"].append(f"Incorrect CSV headers: {headers}")
        except Exception as e:
            result["details"].append(f"Error reading CSV: {str(e)}")
    else:
        result["details"].append("CSV file does not exist.")

    with open(os.path.join(base_dir, "verify_result.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
