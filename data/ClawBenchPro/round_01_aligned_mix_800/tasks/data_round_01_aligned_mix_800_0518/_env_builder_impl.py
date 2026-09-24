import os
import json
import random
import csv

def build_env():
    # 1. Create directory structure
    dirs = [
        "vault/logs",
        "archive/internal/catalog/fragments",
        "deliverables"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 2. Generate Fragmented Ingredient Data
    ingredients_pool = [
        ("Lavender Oil", "natural"), ("Beeswax", "natural"), ("Coconut Oil", "natural"),
        ("Rose Water", "natural"), ("Aloe Vera", "natural"), ("Shea Butter", "natural"),
        ("Vitamin E", "natural"), ("Jojoba Oil", "natural"), ("Tea Tree Oil", "natural"),
        ("Honey", "natural"), ("Argan Oil", "natural"), ("Chamomile", "natural"),
        ("Dimethicone", "synthetic"), ("Parabens", "synthetic"), ("Phthalates", "synthetic"),
        ("Sodium Lauryl Sulfate", "synthetic"), ("Petrolatum", "synthetic"), ("Mineral Oil", "synthetic"),
        ("Formaldehyde", "synthetic"), ("Oxybenzone", "synthetic")
    ]
    
    # Shuffle and split into 5 fragments (JSON, CSV, TXT)
    random.shuffle(ingredients_pool)
    for i in range(5):
        fragment = ingredients_pool[i*4 : (i+1)*4]
        filename = f"part_{i+1}_ref"
        if i % 2 == 0:
            with open(f"archive/internal/catalog/fragments/{filename}.json", "w") as f:
                json.dump([{"ing": x[0], "cat": x[1]} for x in fragment], f)
        else:
            with open(f"archive/internal/catalog/fragments/{filename}.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["item", "class"])
                for x in fragment:
                    writer.writerow(x)

    # 3. Generate Massive Recipe Noise
    # The "True Winner"
    winner = {
        "name": "Project_Phoenix_Final",
        "ingredients": ["Lavender Oil", "Shea Butter", "Honey"],
        "ph": 5.45,
        "score": 9.8
    }
    
    # Create 500 files. One is the winner, others are decoys.
    for i in range(500):
        is_winner = (i == 237) # Hide the winner at a specific index
        if is_winner:
            recipe = winner
        else:
            # Generate decoys
            # Some fail pH, some fail purity, some have low scores
            fail_type = random.choice(["ph_low", "ph_high", "synthetic", "low_score"])
            recipe = {
                "name": f"Prototype_{i:03d}_{random.randint(1000,9999)}",
                "ingredients": random.sample([x[0] for x in ingredients_pool], random.randint(2, 4)),
                "ph": random.uniform(3.0, 4.9) if fail_type == "ph_low" else (random.uniform(6.1, 9.0) if fail_type == "ph_high" else random.uniform(5.0, 6.0)),
                "score": random.uniform(1.0, 9.0) if fail_type != "low_score" else random.uniform(1.0, 5.0)
            }
            # Ensure synthetic if fail_type is synthetic
            if fail_type == "synthetic":
                recipe["ingredients"].append("Dimethicone")
            else:
                # Ensure it stays natural if not synthetic fail
                recipe["ingredients"] = [ing for ing in recipe["ingredients"] if any(ing == p[0] and p[1] == "natural" for p in ingredients_pool)]
                if not recipe["ingredients"]: recipe["ingredients"] = ["Beeswax"]

        # Vary file formats for recipes to increase extraction difficulty
        file_ext = random.choice(["log", "txt", "tmp"])
        file_path = f"vault/logs/batch_{i:03d}.{file_ext}"
        
        content_templates = [
            f"RECIPE: {recipe['name']}\nDATA_POINT_PH: {recipe['ph']}\nQUALITY_VAL: {recipe['score']}\nCOMPONENTS: {', '.join(recipe['ingredients'])}",
            f"--- LOG START ---\nID: {recipe['name']}\nRESULT: {recipe['score']} (Efficacy)\nPH_SENSOR: {recipe['ph']}\nINGR: {';'.join(recipe['ingredients'])}\n--- END ---",
            f"METRICS|{recipe['name']}|{recipe['ph']}|{recipe['score']}|{'+'.join(recipe['ingredients'])}"
        ]
        
        with open(file_path, "w") as f:
            f.write(random.choice(content_templates))

if __name__ == "__main__":
    build_env()
