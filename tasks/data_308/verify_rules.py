import os
import json

def verify():
    base_dir = "."
    state = {
        "eco_crafts_exists": False,
        "points_file_exists": False,
        "json_valid": False,
        "points_correct": False,
        "all_valid_crafts_present": False,
        "no_invalid_crafts": False
    }

    json_path = os.path.join(base_dir, "eco_crafts.json")
    points_path = os.path.join(base_dir, "points.txt")

    if os.path.exists(json_path):
        state["eco_crafts_exists"] = True
        try:
            with open(json_path, "r") as f:
                data = json.load(f)
            state["json_valid"] = True
            
            valid_names = {
                "Cardboard Castle", 
                "Cotton Friendship Bracelets", 
                "Pinecone Animals", 
                "Leaf Art", 
                "Acorn People", 
                "Rock Painting"
            }
            invalid_names = {
                "Bottle Planter", 
                "Sparkly Ornaments", 
                "Brillantina Slime", 
                "Plastico Wind Chime"
            }
            
            found_names = {item.get("name") for item in data if isinstance(item, dict)}
            
            if valid_names.issubset(found_names):
                state["all_valid_crafts_present"] = True
            
            if len(invalid_names.intersection(found_names)) == 0:
                state["no_invalid_crafts"] = True

        except Exception as e:
            pass

    if os.path.exists(points_path):
        state["points_file_exists"] = True
        try:
            with open(points_path, "r") as f:
                points = int(f.read().strip())
            if points == 200:
                state["points_correct"] = True
        except:
            pass

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
