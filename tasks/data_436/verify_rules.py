import os
import csv
import json

def verify():
    base_dir = "."
    results = {
        "grades_csv_exists": False,
        "grades_correct": False,
        "recipes_folder_exists": False,
        "recipe_moved": False,
        "score": 0
    }
    
    csv_path = os.path.join(base_dir, "consolidated_grades.csv")
    if os.path.exists(csv_path):
        results["grades_csv_exists"] = True
        try:
            with open(csv_path, "r") as f:
                reader = csv.reader(f)
                header = next(reader)
                grades = {}
                for row in reader:
                    if len(row) >= 2:
                        name = row[0].strip().capitalize()
                        val = float(row[1].strip())
                        grades[name] = val
            
            expected = {
                "Alice": 80.0,
                "Bob": 92.0,
                "John": 86.5,
                "Sarah": 92.5
            }
            if grades == expected:
                results["grades_correct"] = True
        except Exception:
            pass
            
    recipes_dir = os.path.join(base_dir, "recipes")
    if os.path.exists(recipes_dir) and os.path.isdir(recipes_dir):
        results["recipes_folder_exists"] = True
        if os.path.exists(os.path.join(recipes_dir, "dinner_ideas.txt")):
            results["recipe_moved"] = True
            
    score = 0
    if results["grades_csv_exists"]: score += 20
    if results["grades_correct"]: score += 50
    if results["recipes_folder_exists"]: score += 10
    if results["recipe_moved"]: score += 20
    
    results["score"] = score
    
    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    verify()
