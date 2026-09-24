import os
import json

def verify():
    state = {
        "portfolio_exists": False,
        "is_valid_json": False,
        "contains_valid_poem1": False,
        "contains_valid_poem5": False,
        "excludes_spanish_poem": True,
        "excludes_todo_poem": True,
        "excludes_nervous_poem": True,
        "correct_line_count": False
    }

    portfolio_path = "submission/final_portfolio.json"
    
    if os.path.exists(portfolio_path):
        state["portfolio_exists"] = True
        
        try:
            with open(portfolio_path, "r", encoding="utf-8") as f:
                content = f.read()
                data = json.loads(content)
                state["is_valid_json"] = True
                
                content_lower = content.lower()
                
                if "a sunny day" in content_lower:
                    state["contains_valid_poem1"] = True
                if "nature's peace" in content_lower or "nature s peace" in content_lower:
                    state["contains_valid_poem5"] = True
                    
                if "el sol" in content_lower or "brillante" in content_lower:
                    state["excludes_spanish_poem"] = False
                if "writer's block" in content_lower or "todo:" in content_lower:
                    state["excludes_todo_poem"] = False
                if "anxiety" in content_lower or "nervous" in content_lower:
                    state["excludes_nervous_poem"] = False

                # Total lines of valid poems (4 lines each, total 8 lines of poetry text)
                def find_8(obj):
                    if isinstance(obj, dict):
                        return any(find_8(v) for v in obj.values())
                    elif isinstance(obj, list):
                        return any(find_8(v) for v in obj)
                    elif isinstance(obj, int) and obj == 8:
                        return True
                    elif isinstance(obj, str) and obj.strip() == "8":
                        return True
                    return False
                
                if find_8(data):
                    state["correct_line_count"] = True

        except Exception:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
