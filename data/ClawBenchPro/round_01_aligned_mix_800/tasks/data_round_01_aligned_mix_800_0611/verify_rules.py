import os
import json

def verify():
    state = {
        "results_folder_exists": False,
        "playlist_file_exists": False,
        "playlist_correct_tracks": False,
        "playlist_no_slow_tracks": False,
        "costs_file_exists": False,
        "costs_correct_sum": False
    }

    if os.path.isdir("results"):
        state["results_folder_exists"] = True

    playlist_path = "results/workout_playlist.txt"
    if os.path.isfile(playlist_path):
        state["playlist_file_exists"] = True
        with open(playlist_path, "r") as f:
            content = f.read().lower()
            
            # BPM > 120 tracks: Iron Will, Adrenaline Rush, Heavy Lifts, Max Reps
            has_fast = all(track in content for track in ["iron will", "adrenaline rush", "heavy lifts", "max reps"])
            state["playlist_correct_tracks"] = has_fast
            
            # BPM <= 120 tracks: Soft Lullaby, Windshield Wipers In The Rain, Sunday Morning
            has_slow = any(track in content for track in ["soft lullaby", "windshield wipers", "sunday morning"])
            state["playlist_no_slow_tracks"] = not has_slow

    costs_path = "results/windshield_costs.txt"
    if os.path.isfile(costs_path):
        state["costs_file_exists"] = True
        with open(costs_path, "r") as f:
            content = f.read()
            # Windshield costs: 210.50 + 185.25 + 230.00 = 625.75
            if "625.75" in content:
                state["costs_correct_sum"] = True

    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
