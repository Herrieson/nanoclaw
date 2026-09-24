import os
import json

def verify():
    state = {
        "shortlist_exists": False,
        "is_valid_json": False,
        "contains_valid_bands": False,
        "excludes_scandals": True,
        "excludes_over_budget": True,
        "excludes_blacklist": True,
        "excludes_wrong_genre": True
    }

    target_file = "deliverables/shortlist.json"
    
    if os.path.exists(target_file):
        state["shortlist_exists"] = True
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                state["is_valid_json"] = True
                
                content_str = json.dumps(data).lower()
                
                # Check valid bands: Neon Echoes, The Crimson Void, Fading Light, Electric Dreams
                if "neon echoes" in content_str and "fading light" in content_str:
                    state["contains_valid_bands"] = True
                
                # Check constraints
                if "rebel yell" in content_str or "pop sensations" in content_str:
                    state["excludes_scandals"] = False
                    
                if "midnight runners" in content_str:
                    state["excludes_over_budget"] = False
                    
                if "the blacklisted" in content_str:
                    state["excludes_blacklist"] = False
                    
                if "static noise" in content_str:
                    state["excludes_wrong_genre"] = False

        except Exception:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
