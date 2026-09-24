import os
import json

def verify():
    state = {
        "fixed_assets_folder_exists": False,
        "mod_pack_file_exists": False,
        "is_valid_json": False,
        "has_frostbite_sword": False,
        "has_cheese_crown": False,
        "has_cranberry_potion": False,
        "contains_lame_axe": False,
        "contains_basic_boots": False
    }

    folder_path = "fixed_assets"
    file_path = os.path.join(folder_path, "my_mod_pack.json")

    if os.path.isdir(folder_path):
        state["fixed_assets_folder_exists"] = True

    if os.path.isfile(file_path):
        state["mod_pack_file_exists"] = True
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["is_valid_json"] = True
            
            data_str = json.dumps(data).lower()
            
            if "frostbite sword" in data_str and "#00ffff" in data_str:
                state["has_frostbite_sword"] = True
            if "cheese crown" in data_str and "#ffd700" in data_str:
                state["has_cheese_crown"] = True
            if "cranberry potion" in data_str and "#aa0033" in data_str:
                state["has_cranberry_potion"] = True
                
            if "lame axe" in data_str or "#ff0000" in data_str:
                state["contains_lame_axe"] = True
            if "basic boots" in data_str or "#888888" in data_str:
                state["contains_basic_boots"] = True

        except Exception:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
