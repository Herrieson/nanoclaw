import os
import sys
import json
import re

def calculate_score():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1. Check Output Files Existence
    urgent_care_path = os.path.join(workspace, "reports/urgent_care.txt")
    feed_report_path = os.path.join(workspace, "reports/feed_summary.txt") # Based on prompt hint for reports/ folder
    
    # Note: Prompt asked for two files in reports/, let's check what was actually asked
    # File 1: reports/urgent_care.txt
    # File 2: implied feed record report (the prompt says "get those two files into the reports/ folder")
    # We will look for anything that looks like a feed report if the second one isn't named exactly.
    
    # Step 1: Urgent Care File (Animal IDs) - 50 points
    if os.path.exists(urgent_care_path):
        with open(urgent_care_path, "r") as f:
            content = f.read()
        
        # Expected IDs: Cow-402, Horse-X9, Sheep-112, Pig-05
        # Must NOT include 2022 data or 2023-09 data.
        expected_ids = {"Cow-402", "Horse-X9", "Sheep-112", "Pig-05"}
        # Some random noise IDs from 2023-09 logs would be 3-digit numbers
        
        found_ids = set(re.findall(r'[A-Za-z]+-\w+', content))
        
        correct_ids = found_ids.intersection(expected_ids)
        wrong_ids = found_ids.difference(expected_ids)
        
        id_score = (len(correct_ids) / len(expected_ids)) * 40
        if len(wrong_ids) > 0:
            id_score -= min(20, len(wrong_ids) * 5) # Penalize for noise
        
        id_score = max(0, id_score)
        score += id_score
        details.append({
            "item": "Animal ID Extraction (Urgent Care)",
            "score": int(id_score),
            "max_score": 50,
            "passed": id_score >= 30,
            "reason": f"Found {len(correct_ids)}/4 correct IDs. Found {len(wrong_ids)} noise IDs."
        })
        
        # Structure check (clean list)
        if len(content.splitlines()) >= 4:
            score += 10
            details.append({"item": "Urgent Care Format", "score": 10, "max_score": 10, "passed": True, "reason": "List format maintained"})
        else:
            details.append({"item": "Urgent Care Format", "score": 0, "max_score": 10, "passed": False, "reason": "List too short or poorly formatted"})
    else:
        details.append({"item": "Urgent Care File Existence", "score": 0, "max_score": 50, "passed": False, "reason": "reports/urgent_care.txt not found"})

    # Step 2: Feed Calculation (Alfalfa Total) - 40 points
    # Calculation: 1250.5 (CSV) + 949.5 (JSON/TXT) + 800 (Text) = 3000.0
    found_feed_file = None
    for filename in os.listdir(os.path.join(workspace, "reports")):
        if "feed" in filename.lower() or "alfalfa" in filename.lower():
            found_feed_file = os.path.join(workspace, "reports", filename)
            break
    
    if found_feed_file:
        with open(found_feed_file, "r") as f:
            feed_content = f.read()
        
        # Look for the number 3000
        if "3000" in feed_content:
            score += 40
            details.append({"item": "Feed Calculation", "score": 40, "max_score": 40, "passed": True, "reason": "Correct total (3000 lbs) found in report"})
        elif "2200" in feed_content or "2050" in feed_content: # Partial matches if they missed one source
            score += 15
            details.append({"item": "Feed Calculation", "score": 15, "max_score": 40, "passed": False, "reason": "Partial total found. Likely missed one data source (CSV, JSON, or Text)"})
        else:
            details.append({"item": "Feed Calculation", "score": 0, "max_score": 40, "passed": False, "reason": "Correct total (3000) not found"})
    else:
        # Check if they put it in a different file or just named it weirdly
        details.append({"item": "Feed Report Existence", "score": 0, "max_score": 40, "passed": False, "reason": "No feed report found in reports/ folder"})

    # Final Summary
    final_score = min(100, max(0, int(score)))
    output = {
        "total_score": final_score,
        "details": details
    }
    
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    calculate_score()
