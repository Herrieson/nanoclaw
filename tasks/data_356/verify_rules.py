import os
import csv
import json

def verify():
    base_dir = "."
    csv_path = os.path.join(base_dir, "recommended_products.csv")
    
    result = {
        "csv_exists": False,
        "headers_correct": False,
        "correct_products": False,
        "correct_ratings": False,
        "errors": []
    }
    
    if not os.path.exists(csv_path):
        result["errors"].append("recommended_products.csv not found.")
        print(json.dumps(result))
        return
        
    result["csv_exists"] = True
    
    expected_products = {
        "PROD-003": {"name": "Urban Compost Bin", "supplier": "GreenLife", "avg": 4.67}, # (5+4+5)/3 = 4.666...
        "PROD-005": {"name": "Reusable Hemp Tote Bags", "supplier": "EcoGear Co", "avg": 5.0} # (5+5)/2 = 5.0
    }
    
    # PROD-001: (5+2+4)/3 = 3.66 (fails rating < 4)
    # PROD-002: 4.0 (fails cert)
    # PROD-004: 4.0 (fails cert - Self-Declared)
    # PROD-006: (2+5)/2 = 3.5 (fails rating)
    # PROD-007: 1.0 (fails rating & cert)
    
    found_products = {}
    
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)
            if [h.strip() for h in headers] == ["ProductID", "ProductName", "Supplier", "AverageRating"]:
                result["headers_correct"] = True
            else:
                result["errors"].append(f"Incorrect headers: {headers}")
                
            for row in reader:
                if len(row) == 4:
                    pid, pname, psupp, pavg = [x.strip() for x in row]
                    try:
                        found_products[pid] = float(pavg)
                    except ValueError:
                        result["errors"].append(f"Invalid rating format for {pid}: {pavg}")
    except Exception as e:
        result["errors"].append(f"Error reading CSV: {str(e)}")
        print(json.dumps(result))
        return

    # Check products
    expected_ids = set(expected_products.keys())
    found_ids = set(found_products.keys())
    
    if expected_ids == found_ids:
        result["correct_products"] = True
    else:
        result["errors"].append(f"Expected products {expected_ids}, but found {found_ids}")
        
    # Check ratings (allow minor rounding differences, e.g., 4.67)
    rating_correct = True
    for pid in expected_ids:
        if pid in found_products:
            if abs(found_products[pid] - expected_products[pid]["avg"]) > 0.05:
                rating_correct = False
                result["errors"].append(f"Incorrect rating for {pid}: expected ~{expected_products[pid]['avg']}, got {found_products[pid]}")
    
    if result["correct_products"] and rating_correct:
        result["correct_ratings"] = True

    print(json.dumps(result))

if __name__ == "__main__":
    verify()
