import os
import json
import re

def verify():
    workspace = "."
    if not os.path.exists(workspace):
        workspace = "." # Fallback for local testing

    state = {
        "medical_folder_exists": False,
        "vintage_folder_exists": False,
        "medical_files_correct": False,
        "vintage_files_correct": False,
        "summary_exists": False,
        "summary_correct": False,
        "records_folder_empty": False
    }

    medical_dir = os.path.join(workspace, "medical")
    vintage_dir = os.path.join(workspace, "vintage")
    records_dir = os.path.join(workspace, "records")
    summary_file = os.path.join(workspace, "summary.txt")

    # Check directories
    state["medical_folder_exists"] = os.path.isdir(medical_dir)
    state["vintage_folder_exists"] = os.path.isdir(vintage_dir)

    # Check file contents of directories
    expected_medical = {"doc1.txt", "doc4.txt", "doc6.txt", "doc7.txt"}
    expected_vintage = {"doc2.txt", "doc3.txt", "doc5.txt"}

    if state["medical_folder_exists"]:
        actual_medical = set(os.listdir(medical_dir))
        state["medical_files_correct"] = actual_medical == expected_medical

    if state["vintage_folder_exists"]:
        actual_vintage = set(os.listdir(vintage_dir))
        state["vintage_files_correct"] = actual_vintage == expected_vintage

    # Check if records folder is empty or deleted
    if not os.path.exists(records_dir) or len(os.listdir(records_dir)) == 0:
        state["records_folder_empty"] = True

    # Check summary
    if os.path.isfile(summary_file):
        state["summary_exists"] = True
        with open(summary_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            # 450 + 120 + 85 = 655
            if "Total Vintage Value: $655" in content:
                state["summary_correct"] = True

    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
