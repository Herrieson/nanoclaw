import os
import re
import json

def verify():
    base_dir = "."
    itinerary_path = os.path.join(base_dir, "itinerary.txt")
    
    result = {
        "file_exists": False,
        "total_distance": None,
        "contains_polluted_areas": False,
        "raw_content": ""
    }
    
    if os.path.exists(itinerary_path):
        result["file_exists"] = True
        with open(itinerary_path, "r") as f:
            content = f.read()
            result["raw_content"] = content
            
        # Check for total distance
        match = re.search(r'Total Distance:\s*(\d+)\s*miles', content, re.IGNORECASE)
        if match:
            result["total_distance"] = int(match.group(1))
            
        # Check for polluted areas
        polluted = ["Smog Valley", "Plasticville"]
        for p in polluted:
            if p.lower() in content.lower():
                result["contains_polluted_areas"] = True
                
    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
