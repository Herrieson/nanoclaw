import os
import json

def verify():
    output_file = "weekend_sauces.txt"
    state = {
        "output_file_exists": False,
        "contains_devils_tears": False,
        "contains_midwest_meltdown": False,
        "contains_wimpy": False,
        "contains_bankrupt": False,
        "correct_cost_devils": False,
        "correct_cost_midwest": False,
        "raw_content": ""
    }

    if os.path.exists(output_file):
        state["output_file_exists"] = True
        with open(output_file, "r") as f:
            content = f.read().lower()
            state["raw_content"] = content

            if "devil's tears" in content or "devils tears" in content:
                state["contains_devils_tears"] = True
            if "midwest meltdown" in content:
                state["contains_midwest_meltdown"] = True
            if "wimpy ketchup" in content:
                state["contains_wimpy"] = True
            if "bankrupt burner" in content:
                state["contains_bankrupt"] = True

            if "9.00" in content or "9.0" in content or "9$" in content or "$9" in content:
                state["correct_cost_devils"] = True
            if "7.00" in content or "7.0" in content or "7$" in content or "$7" in content:
                state["correct_cost_midwest"] = True

    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
