import os
import json
import csv

def verify():
    base_dir = "."
    state = {
        "donations_csv_exists": False,
        "donations_csv_valid": False,
        "playlist_txt_exists": False,
        "playlist_txt_valid": False,
        "errors": []
    }

    donations_path = os.path.join(base_dir, "cleaned_donations.csv")
    playlist_path = os.path.join(base_dir, "mexican_playlist.txt")

    # Verify Donations
    if os.path.exists(donations_path):
        state["donations_csv_exists"] = True
        expected_amounts = [500, 200, 1500, 300, 450, 800.5, 1200, 5000, 100]
        try:
            with open(donations_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                amounts = []
                for row in reader:
                    amounts.append(float(row["Amount"]))
                if amounts == expected_amounts:
                    state["donations_csv_valid"] = True
                else:
                    state["errors"].append(f"Amounts mismatch. Expected: {expected_amounts}, Got: {amounts}")
        except Exception as e:
            state["errors"].append(f"Error parsing donations CSV: {str(e)}")
    else:
        state["errors"].append("cleaned_donations.csv not found.")

    # Verify Playlist
    if os.path.exists(playlist_path):
        state["playlist_txt_exists"] = True
        expected_songs = [
            "Cielito Lindo",
            "El Rey",
            "La Chona",
            "El Sinaloense",
            "Volver Volver",
            "Caminos de Michoacán"
        ]
        try:
            with open(playlist_path, "r", encoding="utf-8") as f:
                songs = [line.strip() for line in f if line.strip()]
            if songs == expected_songs:
                state["playlist_txt_valid"] = True
            else:
                state["errors"].append(f"Playlist mismatch. Expected: {expected_songs}, Got: {songs}")
        except Exception as e:
            state["errors"].append(f"Error parsing playlist TXT: {str(e)}")
    else:
        state["errors"].append("mexican_playlist.txt not found.")

    with open("verify_result.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
