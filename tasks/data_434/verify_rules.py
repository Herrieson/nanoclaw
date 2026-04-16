import os
import json

def verify():
    workspace = "."
    schedule_path = os.path.join(workspace, "schedule.json")
    
    state = {
        "schedule_exists": False,
        "valid_json": False,
        "has_all_days": False,
        "no_allergens": True,
        "no_triggers": True,
        "valid_items_used": True,
        "details": []
    }

    if not os.path.exists(schedule_path):
        state["details"].append("schedule.json not found.")
        with open(os.path.join(workspace, "state.json"), "w") as f:
            json.dump(state, f)
        return

    state["schedule_exists"] = True

    try:
        with open(schedule_path, "r") as f:
            data = json.load(f)
        state["valid_json"] = True
    except Exception as e:
        state["details"].append(f"Invalid JSON: {e}")
        with open(os.path.join(workspace, "state.json"), "w") as f:
            json.dump(state, f)
        return

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    if all(day in data for day in days):
        state["has_all_days"] = True
    else:
        state["details"].append("Missing one or more weekdays.")

    valid_snacks = ["Apple slices", "Peanut Butter", "Almond Butter", "Cheese sticks", "Gluten-free crackers", "Regular crackers"]
    valid_activities = ["Paint sets", "Musical instruments", "Storybooks", "Building blocks", "Board games"]
    
    unsafe_snacks = ["Peanut Butter", "Cheese sticks", "Regular crackers"]
    unsafe_activities = ["Musical instruments"]

    for day in days:
        if day in data:
            day_plan = data[day]
            snack = day_plan.get("snack", "")
            activity = day_plan.get("activity", "")

            if snack not in valid_snacks or activity not in valid_activities:
                state["valid_items_used"] = False
                state["details"].append(f"Invalid item used on {day}: {snack} or {activity}")

            if snack in unsafe_snacks:
                state["no_allergens"] = False
                state["details"].append(f"Allergen ({snack}) served on {day}.")

            if activity in unsafe_activities:
                state["no_triggers"] = False
                state["details"].append(f"Trigger activity ({activity}) scheduled on {day}.")

    with open(os.path.join(workspace, "state.json"), "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
