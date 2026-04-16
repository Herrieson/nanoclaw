import os
import json
import re

def verify():
    base_dir = "."
    country_hits_dir = os.path.join(base_dir, "Country_Hits")
    messy_dir = os.path.join(base_dir, "messy_desktop")
    earnings_file = os.path.join(base_dir, "total_earnings.txt")
    
    state = {
        "country_hits_dir_exists": False,
        "lyric_files_moved": 0,
        "lyric_files_left_in_messy": 0,
        "earnings_file_exists": False,
        "earnings_sum_correct": False,
        "extracted_sum": None
    }
    
    keywords = ["whiskey", "pickup truck", "heartbreak"]
    
    # Check Country_Hits directory
    if os.path.isdir(country_hits_dir):
        state["country_hits_dir_exists"] = True
        for root, _, files in os.walk(country_hits_dir):
            for file in files:
                with open(os.path.join(root, file), 'r', errors='ignore') as f:
                    content = f.read().lower()
                    if any(kw in content for kw in keywords):
                        state["lyric_files_moved"] += 1

    # Check if messy_desktop still has lyric files
    if os.path.isdir(messy_dir):
        for root, _, files in os.walk(messy_dir):
            for file in files:
                with open(os.path.join(root, file), 'r', errors='ignore') as f:
                    content = f.read().lower()
                    if any(kw in content for kw in keywords):
                        state["lyric_files_left_in_messy"] += 1

    # Check total earnings
    expected_sum = 1122.17
    if os.path.isfile(earnings_file):
        state["earnings_file_exists"] = True
        with open(earnings_file, 'r', errors='ignore') as f:
            content = f.read().strip()
            # Find the first number in the file
            match = re.search(r'\d+\.\d{2}', content)
            if match:
                val = float(match.group())
                state["extracted_sum"] = val
                if abs(val - expected_sum) < 0.01:
                    state["earnings_sum_correct"] = True

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
