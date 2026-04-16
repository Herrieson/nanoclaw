import os
import json

def verify():
    results = {
        "file_exists": False,
        "valid_json": False,
        "correct_count": 0,
        "correct_prices": False,
        "correct_nutri_codes": False
    }

    file_path = "final_inventory_recovery.json"
    if os.path.exists(file_path):
        results["file_exists"] = True
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            results["valid_json"] = True
            
            if isinstance(data, list):
                results["correct_count"] = len(data)
                
                # 检查折扣后的价格 (original * 0.85)
                # "The Green Alchemist": 45.00 -> 38.25
                # "Sprouts & Spirits": 29.95 -> 25.46
                # "Fermentation Secrets": 55.50 -> 47.18
                # "Raw Vitality": 32.00 -> 27.20
                expected_prices = {
                    "The Green Alchemist": 38.25,
                    "Sprouts & Spirits": 25.46,
                    "Fermentation Secrets": 47.18,
                    "Raw Vitality": 27.20
                }
                
                price_check = True
                code_check = True
                codes = {"NC-9921", "NC-4432", "NC-1029", "NC-8876"}
                found_codes = set()

                for item in data:
                    title = item.get("title")
                    if title in expected_prices:
                        if abs(item.get("price", 0) - expected_prices[title]) > 0.01:
                            price_check = False
                    found_codes.add(item.get("nutri_code"))
                
                results["correct_prices"] = price_check
                results["correct_nutri_codes"] = (found_codes == codes)

        except Exception:
            pass

    with open("state.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
