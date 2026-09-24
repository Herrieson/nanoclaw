import sys
import json

def get_ledger_data(file_path):
    # Mocking the OCR process for Building A
    if "building_a.pdf" in file_path:
        data = [
            {"Date": "2023-07-01", "TenantID": "T001", "Amount": 1200, "Note": "Paid"},
            {"Date": "2023-08-01", "TenantID": "T001", "Amount": 1200, "Note": "Paid"},
            {"Date": "2023-09-01", "TenantID": "T001", "Amount": 1200, "Note": "Late"},
            {"Date": "2023-07-05", "TenantID": "T002", "Amount": 1500, "Note": "Check"},
            {"Date": "2023-08-05", "TenantID": "T002", "Amount": 1500, "Note": "Check"},
            {"Date": "2023-09-10", "TenantID": "T002", "Amount": 1000, "Note": "Partial"}
        ]
        return json.dumps(data)
    else:
        return json.dumps({"error": "File format not supported or file not found."})

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(get_ledger_data(sys.argv[1]))
