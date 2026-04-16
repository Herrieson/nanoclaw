import sqlite3
import json
import os

def verify():
    results = {
        "db_rates_fixed": False,
        "sq_ft_updated": False,
        "json_generated": False,
        "calculation_correct": False
    }
    
    db_path = "evergreen.db"
    json_path = "quotes_to_send.json"
    
    try:
        # Check DB
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check Margaret (Complex-Landscape should be 85.0)
            cursor.execute("SELECT base_rate, sq_ft FROM clients WHERE name='Margaret Henderson'")
            row = cursor.fetchone()
            if row and row[0] == 85.0 and row[1] == 2500:
                results["db_rates_fixed"] = True
                results["sq_ft_updated"] = True
            conn.close()

        # Check JSON output
        if os.path.exists(json_path):
            results["json_generated"] = True
            with open(json_path, 'r') as f:
                data = json.load(f)
                # Formula: (Base * Sqft) * Multiplier
                # Margaret: (85.0 * 2500) * 2.0 = 425000.0
                for entry in data:
                    if entry.get("name") == "Margaret Henderson":
                        if float(entry.get("quote", 0)) == 425000.0:
                            results["calculation_correct"] = True
    except Exception as e:
        results["error"] = str(e)

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
