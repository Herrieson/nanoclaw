import sys
import json

def decode_payload(payload):
    # A mocked domain-specific parsing logic for the DIY Pi Scanner
    mock_db = {
        "7a9b2_SC_45": {"name": "Sarah Connor", "hours": 4.5},
        "3c4d5_ER_30": {"name": "Ellen Ripley", "hours": 3.0},
        "1e2f3_JS_25": {"name": "John Smith", "hours": 2.5},
        "9b8a7_MD_80": {"name": "Miles Dyson", "hours": 8.0},
        "6f5e4_T8_120": {"name": "T-800", "hours": 12.0},
        "2a1b9_SC_15": {"name": "Sarah Connor", "hours": 1.5}
    }
    
    if payload in mock_db:
        return json.dumps(mock_db[payload], indent=2)
    else:
        return json.dumps({"error": "Unknown or corrupted payload. Cannot decode."})

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing payload parameter."}))
    else:
        print(decode_payload(sys.argv[1]))
