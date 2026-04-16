import os
import json
import re

def verify():
    base_dir = "."
    quote_file = os.path.join(base_dir, "best_quote.txt")
    
    state = {
        "file_exists": False,
        "content": "",
        "found_supplier": None,
        "found_price": None,
        "is_correct_supplier": False,
        "is_correct_price": False
    }

    if os.path.exists(quote_file):
        state["file_exists"] = True
        with open(quote_file, 'r') as f:
            content = f.read().strip()
            state["content"] = content
            
            # Simple heuristic to extract info
            content_lower = content.lower()
            
            if "southern_timber" in content_lower:
                state["found_supplier"] = "southern_timber"
                state["is_correct_supplier"] = True
                
            # Regex to find any floating point number that looks like a price
            price_match = re.search(r'\b454\.50\b', content)
            if price_match:
                state["found_price"] = 454.50
                state["is_correct_price"] = True

    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
