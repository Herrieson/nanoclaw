import os
import json
import glob

def verify():
    state = {
        "project_brief_dir_exists": False,
        "json_master_list_exists": False,
        "visual_aid_txt_exists": False,
        "json_contains_correct_items": False,
        "visual_aid_contains_ascii_chart": False,
        "visual_aid_contains_correct_totals": False
    }

    brief_dir = "project_brief"
    
    if os.path.exists(brief_dir) and os.path.isdir(brief_dir):
        state["project_brief_dir_exists"] = True

        # Check for JSON file
        json_files = glob.glob(os.path.join(brief_dir, "*.json"))
        if json_files:
            state["json_master_list_exists"] = True
            
            # Verify the content of the JSON list
            # Valid items should be exactly: A01, A02, A05, B02, B05
            try:
                with open(json_files[0], 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Ensure it's a list or dictionary with 5 items
                    valid_item_count = len(data) if isinstance(data, list) else len(data.keys())
                    
                    # Convert json to string to check for IDs or Descriptions
                    data_str = json.dumps(data).upper()
                    has_a01 = "A01" in data_str
                    has_a02 = "A02" in data_str
                    has_b02 = "B02" in data_str
                    has_b05 = "B05" in data_str
                    
                    # Check that invalid items are excluded
                    no_a03 = "A03" not in data_str
                    no_a04 = "A04" not in data_str
                    no_b01 = "B01" not in data_str
                    no_b03 = "B03" not in data_str
                    no_b04 = "B04" not in data_str
                    
                    if valid_item_count == 5 and has_a01 and has_a02 and has_b02 and has_b05 and no_a03 and no_a04 and no_b01 and no_b03 and no_b04:
                        state["json_contains_correct_items"] = True
            except Exception:
                pass

        # Check for Visual Aid Text File
        txt_files = glob.glob(os.path.join(brief_dir, "*.txt"))
        if txt_files:
            state["visual_aid_txt_exists"] = True
            try:
                with open(txt_files[0], 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Check for ASCII chart characteristics
                    if any(char in content for char in ['|', '#', '=', '*', '█']):
                        state["visual_aid_contains_ascii_chart"] = True
                        
                    # Expected totals:
                    # Solar: 150 + 400 = 550
                    # Wind: 300
                    # Hydroponic: 50 + 120 = 170
                    has_solar_total = "550" in content
                    has_wind_total = "300" in content
                    has_hydro_total = "170" in content
                    
                    if has_solar_total and has_wind_total and has_hydro_total:
                        state["visual_aid_contains_correct_totals"] = True
            except Exception:
                pass

    with open("state.json", "w", encoding='utf-8') as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
