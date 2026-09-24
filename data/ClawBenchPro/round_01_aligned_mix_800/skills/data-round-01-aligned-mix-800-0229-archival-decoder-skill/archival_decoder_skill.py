import sys
import json

def decode_file(file_path):
    if not file_path.endswith(".arch"):
        return json.dumps({"error": "Unsupported file format. Only .arch files are supported."})
    
    # Mocking the extraction of data from the proprietary .arch binary format
    extracted_data = [
        {"Call_Number": "ESP-006", "Title": "Old Letters", "Author": "Unknown", "Year": "1899"},
        {"Call_Number": "ESP-006", "Title": "Old Letters", "Author": "Unknown", "Year": "1899"}, # Duplicate
        {"Call_Number": "ESP-007", "Title": "Map of the Port", "Author": "Captain R.", "Year": "1812"}
    ]
    return json.dumps(extracted_data, indent=2)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing file path argument."}))
    else:
        print(decode_file(sys.argv[1]))
