import os
import re
import json

def verify():
    base_dir = "."
    shopping_list_path = os.path.join(base_dir, "shopping_list.txt")
    
    result = {
        "file_exists": False,
        "total_cost_found": False,
        "total_cost_correct": False,
        "extracted_cost": None,
        "suppliers_mentioned": []
    }
    
    if not os.path.exists(shopping_list_path):
        with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
            json.dump(result, f, indent=4)
        return
        
    result["file_exists"] = True
    
    with open(shopping_list_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Check for correct total cost
    # Saffron: 3g * 9.5 = 28.5
    # Arborio Rice: 800g = 0.8kg * 5.0 = 4.0
    # Truffle Oil: 250ml = 0.25L * 100.0 = 25.0
    # Parmesan: 500g = 0.5kg * 20.0 = 10.0
    # Total = 67.50
    
    cost_match = re.search(r'Total Cost:\s*\$([0-9.]+)', content, re.IGNORECASE)
    if cost_match:
        result["total_cost_found"] = True
        cost = float(cost_match.group(1))
        result["extracted_cost"] = cost
        if abs(cost - 67.50) < 0.01:
            result["total_cost_correct"] = True
            
    # Check if cheapest suppliers are mentioned
    expected_suppliers = ["Spice Imports", "Bulk Foods", "Luxury Liquids", "Dairy Farms"]
    for supplier in expected_suppliers:
        if supplier.lower() in content.lower():
            result["suppliers_mentioned"].append(supplier)
            
    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
