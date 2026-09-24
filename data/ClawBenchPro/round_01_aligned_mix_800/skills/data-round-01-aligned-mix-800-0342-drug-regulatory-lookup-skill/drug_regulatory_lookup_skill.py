import sys
import json

def lookup(code, api_type="internal"):
    if api_type == "internal":
        # Simulate a glitchy API as mentioned in the prompt
        return "Error 500: Internal Server Error. Service 'fda_internal_api' is unavailable."
    
    mapping = {
        "CODE-99": "Schedule II (CII)",
        "REG-01": "Schedule VI (Rx)",
        "OTC-FREE": "Over-the-Counter (OTC)"
    }
    
    res = mapping.get(code.upper(), "Unknown")
    return json.dumps({"code": code, "schedule": res})

if __name__ == "__main__":
    # Simple CLI parser
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--class_code", required=True)
    parser.add_argument("--api_type", default="internal")
    args = parser.parse_args()
    
    print(lookup(args.class_code, args.api_type))
