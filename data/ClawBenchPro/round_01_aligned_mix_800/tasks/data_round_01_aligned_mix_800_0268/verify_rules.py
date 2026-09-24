import os
import json

def verify():
    state = {
        "results_folder_exists": False,
        "json_exists": False,
        "json_is_valid": False,
        "txt_exists": False,
        "valid_teams_in_json": False,
        "invalid_teams_not_in_json": False,
        "rejected_teams_in_txt": False,
        "used_correct_skills": False
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
            state["valid_teams_in_json"] = all(team in json_str for team in valid_teams)
            state["invalid_teams_not_in_json"] = all(team not in json_str for team in invalid_teams)
        except:
            pass

    if os.path.isfile(txt_path):
        state["txt_exists"] = True
        try:
            with open(txt_path, "r") as f:
                content = f.read()
            state["rejected_teams_in_txt"] = all(team in content for team in invalid_teams)
        except:
            pass

    # Basic skill usage check in trace is handled by the verify_prompt, 
    # but we can check if the agent at least attempted to call the scripts.
    # This is a placeholder for the verify logic.
    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
