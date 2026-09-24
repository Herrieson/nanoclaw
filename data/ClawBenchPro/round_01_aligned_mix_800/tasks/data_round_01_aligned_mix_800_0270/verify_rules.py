import os
import json
import glob

def verify():
    state = {
        "has_outreach_dir": False,
        "has_json_file": False,
        "has_allocations_section": False,
        "has_shortages_section": False,
        "shortages_correct": False,
        "allocations_valid": False
    }

    if os.path.isdir("outreach_plan"):
        state["has_outreach_dir"] = True
        
        json_files = glob.glob("outreach_plan/*.json")
        if json_files:
            state["has_json_file"] = True
            try:
                with open(json_files[0], "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                # Search for allocations and shortages sections flexibly
                alloc_key = next((k for k in data.keys() if 'allocation' in k.lower()), None)
                short_key = next((k for k in data.keys() if 'shortage' in k.lower()), None)
                
                if alloc_key:
                    state["has_allocations_section"] = True
                if short_key:
                    state["has_shortages_section"] = True
                    
                # Verify shortages calculation
                if short_key:
                    shortages = data[short_key]
                    # Normalize keys by removing spaces and lowercasing
                    norm_shortages = {k.lower().replace(" ", ""): v for k, v in shortages.items()}
                    
                    # Expected Shortages based on batch code evaluation:
                    # Usable Inventory: Beans(50), Blankets(10), Soup(20)
                    # Unusable: Bread(10), Milk(5) -> Usable qty = 0
                    # Needs: Beans(55), Blankets(4), Soup(25), Bread(5), Milk(2)
                    # Shortages: Beans(5), Soup(5), Bread(5), Milk(2), Blankets(0)
                    expected = {
                        "cannedbeans": 5,
                        "cannedsoup": 5,
                        "bread": 5,
                        "milk": 2
                    }
                    
                    shortages_match = True
                    for item, qty in expected.items():
                        if norm_shortages.get(item, 0) != qty:
                            shortages_match = False
                    
                    if norm_shortages.get("blankets", 0) != 0:
                        shortages_match = False
                        
                    state["shortages_correct"] = shortages_match
                    
                # Verify allocations (must not exceed usable inventory)
                if alloc_key:
                    allocations = data[alloc_key]
                    totals = {}
                    for fam, items in allocations.items():
                        if isinstance(items, dict):
                            for item, qty in items.items():
                                norm_item = item.lower().replace(" ", "")
                                totals[norm_item] = totals.get(norm_item, 0) + int(qty)
                    
                    alloc_valid = True
                    if totals.get("cannedbeans", 0) > 50: alloc_valid = False
                    if totals.get("blankets", 0) > 10: alloc_valid = False
                    if totals.get("cannedsoup", 0) > 20: alloc_valid = False
                    if totals.get("bread", 0) > 0: alloc_valid = False
                    if totals.get("milk", 0) > 0: alloc_valid = False
                    
                    state["allocations_valid"] = alloc_valid

            except Exception:
                pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
