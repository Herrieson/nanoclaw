import os
import json

def verify():
    state = {
        "for_sale_dir_exists": False,
        "catalog_json_exists": False,
        "summary_txt_exists": False,
        "grading_standardized": False,
        "missing_price_filled": False,
        "correct_spider_man_kept": False,
        "total_value_correct": False,
        "count_correct": False
    }

    if os.path.exists("for_sale"):
        state["for_sale_dir_exists"] = True
        if os.path.exists("for_sale/catalog.json"):
            state["catalog_json_exists"] = True
        if os.path.exists("for_sale/summary.txt"):
            state["summary_txt_exists"] = True

    # Expected Logic:
    # 1. Spider-Man 129: Compare 9.2 ($2500) vs 9.4 ($2800). Keep 9.4.
    # 2. X-Men 1: 4.5 (Filtered < 6.0)
    # 3. Batman 181: 8.0 ($1500)
    # 4. Fantastic Four 48: 9.0 (Market value from tool should be ~$4500)
    # 5. Iron Man 1: 9.6 ($5000)
    # 6. Green Lantern 76: 8.0 ($800)
    # 7. X-Men 101: 5.5 (Filtered)
    # 8. Avengers 4: 9.0 ($3000)
    
    # Final List: Iron Man 1 (5000), FF 48 (4500), Avengers 4 (3000), Spider-Man 129 (2800), Batman 181 (1500), Green Lantern 76 (800)
    # Total Value: 5000 + 4500 + 3000 + 2800 + 1500 + 800 = 17600
    # Count: 6

    if state["catalog_json_exists"]:
        try:
            with open("for_sale/catalog.json", "r") as f:
                data = json.load(f)
                titles = [item["Title"] for item in data]
                values = [float(item.get("Market_Value", 0)) for item in data]
                
                state["correct_spider_man_kept"] = any(v == 2800 for t, v in zip(titles, values) if t == "The Amazing Spider-Man")
                state["missing_price_filled"] = any(t == "Fantastic Four" and v > 0 for t, v in zip(titles, values))
                state["count_correct"] = (len(data) == 6)
                
                total_v = sum(values)
                if 17000 <= total_v <= 18500: # Allow slight variance due to LLM mock
                    state["total_value_correct"] = True
        except:
            pass

    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
