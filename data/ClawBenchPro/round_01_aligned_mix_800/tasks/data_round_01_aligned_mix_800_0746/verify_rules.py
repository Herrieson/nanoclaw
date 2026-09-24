import os
import json
import re

def verify():
    results = {
        "audit_report_exists": False,
        "ghost_stock_identified": False,
        "revenue_loss_correct": False,
        "dirty_data_filtered": False
    }

    report_path = "audit_reports/summary.json"
    if os.path.exists(report_path):
        results["audit_report_exists"] = True
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
            
            # 1. Check Ghost Stock (DRILL-X: 15-5=10 missing, TRACTOR-09: 1-0=1 missing)
            ghosts = data.get("ghost_stock", [])
            ghost_ids = [g.get("item_id") for g in ghosts]
            if "DRILL-X" in ghost_ids and "TRACTOR-09" in ghost_ids:
                results["ghost_stock_identified"] = True
            
            # 2. Check Revenue Loss Calculation
            # GEN-500 (2 * 4500) + VALVE-22 (1 * 45) = 9045.0
            total_loss = data.get("total_revenue_loss", 0)
            if float(total_loss) == 9045.0:
                results["revenue_loss_correct"] = True

            # 3. Check if they filtered the negative shipment (-5) for PUMP-001
            # If they didn't filter, PUMP-001 would appear as Ghost Stock (Sold 10, Shipped 10-5=5)
            if "PUMP-001" not in ghost_ids:
                results["dirty_data_filtered"] = True
                
        except Exception:
            pass

    with open("state.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
