import sys
import json

def get_valuation(item):
    item = item.lower()
    high_value_keywords = ["gallery", "sculpture", "painting", "yoruba", "exhibition", "showcase"]
    if any(k in item for k in high_value_keywords):
        return {"status": "High Value", "cultural_impact_score": 9.5}
    return {"status": "Standard", "cultural_impact_score": 2.0}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Missing item description")
    else:
        print(json.dumps(get_valuation(sys.argv[1])))
