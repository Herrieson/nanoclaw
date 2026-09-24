import os

def build_env():
    # Create directories
    os.makedirs('shop_notes', exist_ok=True)
    os.makedirs('office_reports', exist_ok=True)

    # Content for the files (Agent will need to use pdf_parser_skill to "read" these)
    # Note: We create files with .pdf extension, though they contain text for the mock tool to read.
    logs = {
        "monday_scan.pdf": "Vehicle: '08 Silverado. Job: Full transmission rebuild. 12 hours. Used 8 quarts of synthetic trans fluid. That heavy duty stuff.",
        "tuesday_scan.pdf": "Vehicle: '15 Civic. Job: Engine oil change. 1 hour. Used 5 quarts of motor oil. Kids are driving me nuts.",
        "wednesday_scan.pdf": "Vehicle: '19 Ford F-250. Job: Transmission flush. 2 hours. 14 quarts of the blue-label fluid. Also did spark plugs on a Camry (3 hrs).",
        "thursday_scan.pdf": "Vehicle: '12 Dodge Ram. Job: Trans solenoid. 4 hours. Lost some fluid, topped off with 3 quarts of the standard red stuff."
    }

    for filename, content in logs.items():
        with open(os.path.join('shop_notes', filename), 'w') as f:
            f.write(content)

if __name__ == '__main__':
    build_env()
