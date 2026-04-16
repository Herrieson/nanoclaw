import os
import json
import re

def verify():
    workspace_dir = "."
    proof_file = os.path.join(workspace_dir, "panther_proof.txt")
    
    result = {
        "has_proof_file": False,
        "found_oak_stump": False,
        "found_mile_marker": False,
        "found_abandoned_trailer": False,
        "no_false_positives": True,
        "score": 0
    }

    if os.path.exists(proof_file):
        result["has_proof_file"] = True
        with open(proof_file, "r", encoding="utf-8") as f:
            content = f.read().lower()
            
            # Check for valid sightings
            if "02/14/2023" in content or "oak stump" in content:
                result["found_oak_stump"] = True
            if "2023-05-10" in content or "mile marker 14" in content:
                result["found_mile_marker"] = True
            if "2023-09-22" in content or "abandoned trailer" in content:
                result["found_abandoned_trailer"] = True
                
            # Check for false positives (wrong county or wrong animal)
            if "lee" in content or "03/01/2023" in content:
                result["no_false_positives"] = False
            if "broward" in content or "2023-08-15" in content:
                result["no_false_positives"] = False
            if "miami-dade" in content or "2023-10-31" in content:
                result["no_false_positives"] = False
            if "bear" in content or "bobcat" in content or "gator" in content:
                 result["no_false_positives"] = False

    # Calculate basic objective score
    score = 0
    if result["has_proof_file"]:
        score += 10
    if result["found_oak_stump"]:
        score += 20
    if result["found_mile_marker"]:
        score += 20
    if result["found_abandoned_trailer"]:
        score += 20
    if result["no_false_positives"] and result["has_proof_file"]:
        score += 30
        
    result["score"] = score

    with open(os.path.join(workspace_dir, "verify_result.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
