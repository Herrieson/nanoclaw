import os
import json

def verify():
    results = {
        "report_exists": False,
        "correct_total_spend": False,
        "correct_most_expensive": False,
        "correct_valuation_increase": False,
        "errors": []
    }

    report_path = "final_report.json" # Expected output location
    
    if not os.path.exists(report_path):
        results["errors"].append("Final report JSON not found.")
        return results

    try:
        with open(report_path, 'r') as f:
            data = json.load(f)
            
        # Calculations:
        # Modern Latin American pieces in Q4 2023:
        # 1. Sol de Esperanza: 45000
        # 2. Ritmo de la Tierra: 65000 (from log)
        # 3. Sueños de Maíz: 38000
        # Total Spend: 45000 + 65000 + 38000 = 148000
        # Most Expensive: Ritmo de la Tierra
        # Valuation: 52000 + 78000 + 41000 = 171000
        # Increase: 171000 - 148000 = 23000

        results["report_exists"] = True
        if abs(data.get("total_spend", 0) - 148000) < 1:
            results["correct_total_spend"] = True
        
        if data.get("most_expensive_item") == "Ritmo de la Tierra":
            results["correct_most_expensive"] = True
            
        if abs(data.get("projected_increase", 0) - 23000) < 1:
            results["correct_valuation_increase"] = True

    except Exception as e:
        results["errors"].append(f"Verification failed with error: {str(e)}")

    with open("state.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
