import os
import json
import sys

def run(brand_name):
    try:
        with open(".hidden_skill_metadata.json", "r") as f:
            mapping = json.load(f)
        
        result = mapping["chemicals"].get(brand_name)
        if result:
            return result
        else:
            return f"No chemical profile found for brand: {brand_name}"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(run(sys.argv[1]))
