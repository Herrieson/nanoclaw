import json

def filipino_recipe_expert_skill(recipe_name):
    traditional = ["Pork Adobo", "Sinigang na Baboy", "Lumpia", "Halo-Halo"]
    fusion = ["Chicken Adobo Fusion", "Sisig Pizza"]
    
    name = recipe_name.strip()
    if name in traditional:
        return json.dumps({"recipe": name, "category": "Traditional Filipino", "is_traditional": True})
    elif name in fusion:
        return json.dumps({"recipe": name, "category": "Filipino Fusion", "is_traditional": False})
    else:
        return json.dumps({"recipe": name, "category": "Unknown", "is_traditional": False})
