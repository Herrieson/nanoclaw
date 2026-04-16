import os
import pandas as pd
from bs4 import BeautifulSoup
import json

def verify():
    results = {
        "html_exists": False,
        "correct_artist_count": 0,
        "encoding_correct": False,
        "no_fake_artists": False,
        "vibe_scores_present": False
    }

    file_path = "final_lineup.html"
    if os.path.exists(file_path):
        results["html_exists"] = True
        with open(file_path, "r", encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            
            # Check for artists (should be 4, 'Fake Artist 1' excluded by label)
            rows = soup.find_all('tr')
            # Assuming first row is header
            artist_names = [td.get_text() for tr in rows for td in tr.find_all('td')[:1]]
            results["correct_artist_count"] = len(artist_names)
            
            # Check for specific encoding fix (e.g., Sueño, Mayagüez)
            full_text = soup.get_text()
            if "Sueño" in full_text and "Mayagüez" in full_text:
                results["encoding_correct"] = True
            
            # Check exclusion logic
            if "Fake Artist 1" not in full_text and "Ghost Label" not in full_text:
                results["no_fake_artists"] = True
            
            # Check if scores (95, 88, etc.) are in the table
            if "95" in full_text and "85" in full_text:
                results["vibe_scores_present"] = True

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
