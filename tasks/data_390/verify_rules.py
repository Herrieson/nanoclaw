import os
import json
import re

def verify():
    result = {
        "potluck_plan_exists": False,
        "selected_safe_recipes": False,
        "avoided_unsafe_recipes": False,
        "garlic_summed_correctly": False,
        "all_ingredients_present": False
    }
    
    plan_path = "potluck_plan.md"
    
    if os.path.exists(plan_path):
        result["potluck_plan_exists"] = True
        with open(plan_path, "r", encoding="utf-8") as f:
            content = f.read().lower()
            
            # Safe recipes: Chicken Adobo, Pork Sinigang, Biko
            has_adobo = "adobo" in content
            has_sinigang = "sinigang" in content
            has_biko = "biko" in content
            
            if has_adobo and has_sinigang and has_biko:
                result["selected_safe_recipes"] = True
                
            # Unsafe: Kare-Kare (peanut), Leche Flan (dairy), Pancit Palabok (shrimp)
            has_unsafe = "kare" in content or "flan" in content or "pancit" in content or "palabok" in content
            if not has_unsafe:
                result["avoided_unsafe_recipes"] = True
                
            # Check sum of garlic: 5 + 3 = 8
            if re.search(r'8\s*cloves', content) or "8" in content.split("garlic")[0][-15:]:
                result["garlic_summed_correctly"] = True
                
            # Check other ingredients presence
            ingredients = ["chicken", "soy sauce", "vinegar", "pork", "tamarind", "tomato", "water spinach", "glutinous rice", "coconut milk", "brown sugar"]
            present_count = sum(1 for i in ingredients if i in content)
            if present_count == len(ingredients):
                result["all_ingredients_present"] = True

    with open("verify_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
