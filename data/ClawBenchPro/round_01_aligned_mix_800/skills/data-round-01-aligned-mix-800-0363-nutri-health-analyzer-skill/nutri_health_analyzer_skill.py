import sys
import json

def analyze(item_name):
    health_db = {
        "organic apples": 95,
        "candy bars": 12,
        "meditation cushions": 100,
        "soda cans": 5,
        "social justice pamphlets": 100,
        "whole wheat bread": 85,
        "processed cheese": 40
    }
    
    name_clean = item_name.lower().strip()
    score = health_db.get(name_clean, 50) # Default to 50 if unknown
    
    result = {
        "item": item_name,
        "health_score": score,
        "recommendation": "Approved" if score > 60 else "Rejected - Too much processing or sugar"
    }
    return json.dumps(result)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python nutri_health_analyzer_skill.py <item_name>")
    else:
        print(analyze(sys.argv[1]))
