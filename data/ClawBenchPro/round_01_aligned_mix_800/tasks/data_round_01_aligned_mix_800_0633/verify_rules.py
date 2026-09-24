import os
import json
import pandas as pd

def verify():
    state = {
        "audit_folder_exists": False,
        "summary_file_exists": False,
        "ghost_payers_identified": False,
        "underpayments_identified": False,
        "total_revenue_correct": False
    }

    results_dir = "audit_results"
    if os.path.exists(results_dir):
        state["audit_folder_exists"] = True
        
        # Check for any common summary file names
        files = os.listdir(results_dir)
        summary_file = None
        for f in files:
            if "summary" in f.lower() or "report" in f.lower():
                summary_file = os.path.join(results_dir, f)
                state["summary_file_exists"] = True
                break
        
        if summary_file:
            try:
                with open(summary_file, 'r') as f:
                    content = f.read().lower()
                    
                    # 1. Identify Ghosts: "Unknown Stranger" and "Zodiac Killer"
                    if "unknown stranger" in content and "zodiac killer" in content:
                        state["ghost_payers_identified"] = True
                    
                    # 2. Identify Underpayment: Robert Brown (800 vs 1100) or Emily Davis (missing month)
                    if "robert brown" in content and "emily davis" in content:
                        state["underpayments_identified"] = True
                    
                    # 3. Calculation Check
                    # Expected total: (1200*3)+(1500*3)+(1100*2+800)+(1800*2)+(1350*3)+(1600*3) + (500+2000)
                    # Master total for 3 months: 25650 (if everyone paid perfectly)
                    # Actual: 
                    # Jan: 8550
                    # Feb: 8750 (8250 real + 500 ghost)
                    # Mar: 7750 (5750 real + 2000 ghost)
                    # Total Actual: 25050
                    if "25050" in content:
                        state["total_revenue_correct"] = True
            except:
                pass

    with open("state.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
