import os
import json

def verify():
    state = {
        "investigation_folder_exists": False,
        "suspects_json_exists": False,
        "json_format_valid": False,
        "caught_bob": False,
        "caught_eve": False,
        "ignored_alice_and_zack": False,
        "bob_minutes_correct": False,
        "eve_minutes_correct": False,
        "bob_approval_correct": False,
        "eve_approval_correct": False
    }

    if os.path.exists("investigation"):
        state["investigation_folder_exists"] = True

    suspects_path = os.path.join("investigation", "suspects.json")
    if os.path.exists(suspects_path):
        state["suspects_json_exists"] = True
        try:
            with open(suspects_path, "r") as f:
                data = json.load(f)
            state["json_format_valid"] = True

            keys = set(data.keys())
            if "Bob" in keys:
                state["caught_bob"] = True
                if data["Bob"].get("total_minutes") == 30:
                    state["bob_minutes_correct"] = True
                if data["Bob"].get("is_approved") is True:
                    state["bob_approval_correct"] = True

            if "Eve" in keys:
                state["caught_eve"] = True
                if data["Eve"].get("total_minutes") == 55:
                    state["eve_minutes_correct"] = True
                if data["Eve"].get("is_approved") is False:
                    state["eve_approval_correct"] = True

            if "Alice" not in keys and "Zack" not in keys and "Charlie" not in keys:
                if keys == {"Bob", "Eve"}:
                    state["ignored_alice_and_zack"] = True

        except Exception:
            pass

    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
