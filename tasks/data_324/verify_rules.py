import os
import json
import re

def verify():
    result = {
        "itinerary_exists": False,
        "distance_calculated": False,
        "distance_accurate": False,
        "found_cabin": False,
        "found_mine": False,
        "found_falls": False,
        "ghost_town_absent": True,
        "chronological_order": False
    }
    
    target_file = "itinerary.txt"
    if os.path.exists(target_file):
        result["itinerary_exists"] = True
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for Distance. Actual distance is ~1.28 km
            # Math: 
            # P1->P2: ~0.21km
            # P2->P3: ~0.21km
            # P3->P4: ~0.28km
            # P4->P5: ~0.27km
            # P5->P6: ~0.29km
            # Total ~ 1.26 - 1.30 km
            dist_match = re.search(r'(\d+\.\d+)', content)
            if dist_match:
                result["distance_calculated"] = True
                dist_val = float(dist_match.group(1))
                if 1.15 <= dist_val <= 1.40:
                    result["distance_accurate"] = True
                    
            # Check Landmarks
            if "Old Settler's Cabin" in content and "pioneers" in content:
                result["found_cabin"] = True
            if "Abandoned Coal Mine" in content and "mining operation" in content:
                result["found_mine"] = True
            if "Whispering Falls" in content and "waterfall" in content:
                result["found_falls"] = True
            if "Ghost Town" in content or "Moonville" in content:
                result["ghost_town_absent"] = False
                
            # Check Chronological Order
            idx_cabin = content.find("Old Settler's Cabin")
            idx_mine = content.find("Abandoned Coal Mine")
            idx_falls = content.find("Whispering Falls")
            
            if 0 <= idx_cabin < idx_mine < idx_falls:
                result["chronological_order"] = True

    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
