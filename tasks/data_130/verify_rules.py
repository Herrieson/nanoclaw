import os
import json

def verify():
    base_dir = "."
    target_file = os.path.join(base_dir, "event_summary.json")
    
    state = {
        "file_exists": False,
        "valid_json": False,
        "winning_film_correct": False,
        "dietary_restrictions_correct": False,
        "parsed_film": None,
        "parsed_diet": None
    }
    
    if os.path.exists(target_file):
        state["file_exists"] = True
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            state["valid_json"] = True
            
            # Expected logic:
            # Yes votes for Modern Times: Alice, Charlie, Fiona, Hannah, Kevin (5)
            # Yes votes for City Lights: Evan, George, Laura (3)
            # Yes votes for The Great Dictator: Jenny (1)
            # Winning film: Modern Times
            
            state["parsed_film"] = data.get("winning_film")
            if str(state["parsed_film"]).strip().lower() == "modern times":
                state["winning_film_correct"] = True
                
            # Expected dietary (Yes only, no 'none' or blank, lowercase, sorted):
            # Alice: vegan
            # Charlie: gluten-free, peanut allergy
            # Evan: lactose intolerant
            # Fiona: vegan
            # George: None (ignore)
            # Hannah: peanut allergy
            # Jenny: gluten-free, dairy free
            # Kevin: blank (ignore)
            # Laura: vegan
            # Unique: ['dairy free', 'gluten-free', 'lactose intolerant', 'peanut allergy', 'vegan']
            
            expected_diet = ['dairy free', 'gluten-free', 'lactose intolerant', 'peanut allergy', 'vegan']
            
            parsed_diet = data.get("dietary_restrictions", [])
            state["parsed_diet"] = parsed_diet
            
            if isinstance(parsed_diet, list):
                # normalize parsed diet for flexible checking
                normalized_parsed = sorted([str(d).strip().lower() for d in parsed_diet])
                if normalized_parsed == expected_diet:
                    state["dietary_restrictions_correct"] = True
                    
        except Exception as e:
            state["error"] = str(e)
            
    with open(os.path.join(base_dir, "state.json"), "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
