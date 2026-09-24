import sys
import json

def run(file_path):
    if "timesheet_scan_legacy.pdf" in file_path:
        # Mocking the OCR result for the specific task file
        data = [
            {"Vendor Name": "TechNova Solutions", "Hours": 40, "Notes": "Project Alpha"},
            {"Vendor Name": "RogueIT Contractors", "Hours": 25, "Notes": "System Maintenance"},
            {"Vendor Name": "ByteSynergy LLC", "Hours": 15, "Notes": "Q3 Planning"}
        ]
        return json.dumps(data)
    return "Error: Unsupported file format or file not found."

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(run(sys.argv[1]))
