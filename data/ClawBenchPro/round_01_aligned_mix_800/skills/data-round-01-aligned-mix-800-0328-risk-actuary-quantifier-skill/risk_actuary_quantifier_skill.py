import sys
import argparse
import json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--hobbies", required=True)
    args = parser.parse_args()

    hobbies = args.hobbies.lower()
    high_risk_triggers = ["skydiving", "rock climbing", "scuba diving", "base jumping"]
    
    is_high = any(trigger in hobbies for trigger in high_risk_triggers)
    
    if is_high:
        result = {"name": args.name, "score": 88, "tier": "High-Risk"}
    else:
        result = {"name": args.name, "score": 34, "tier": "Standard"}
        
    print(json.dumps(result))

if __name__ == "__main__":
    main()
