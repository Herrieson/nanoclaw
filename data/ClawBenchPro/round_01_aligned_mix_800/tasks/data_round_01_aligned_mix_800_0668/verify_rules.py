import os
import json
import sys

def verify():
    state = {
        "results_folder_exists": False,
        "json_exists": False,
        "json_is_valid": False,
        "txt_exists": False,
        "valid_teams_in_json": False,
        "invalid_teams_not_in_json": False,
        "rejected_teams_in_txt": False
    }

    if os.path.isdir("results"):
        state["results_folder_exists"] = True

    json_path = os.path.join("results", "official_bracket.json")
    txt_path = os.path.join("results", "trashed_teams.txt")

    valid_teams = ["Sweat_Lords", "Aim_Assist"]
    invalid_teams = ["Duo_Queue", "Squad_Fam", "Boomers", "Squeakers"]

    if os.path.isfile(json_path):
        state["json_exists"] = True
        try:
            with open(json_path, "r") as f:
                data = json.load(f)
            state["json_is_valid"] = True
            
            json_str = json.dumps(data)
            
            # Check if valid teams are present
            if all(team in json_str for team in valid_teams):
                state["valid_teams_in_json"] = True
                
            # Check if invalid teams are completely absent
            if all(team not in json_str for team in invalid_teams):
                state["invalid_teams_not_in_json"] = True
                
        except Exception:
            pass

    if os.path.isfile(txt_path):
        state["txt_exists"] = True
        try:
            with open(txt_path, "r") as f:
                content = f.read()
            # Check if all rejected teams are in the txt
            if all(team in content for team in invalid_teams):
                state["rejected_teams_in_txt"] = True
        except Exception:
            pass

    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
