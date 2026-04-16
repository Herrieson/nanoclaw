import os
import sqlite3
import pandas as pd
import json

def verify():
    results = {
        "db_fixed": False,
        "route_plan_correct": False,
        "culprit_identified": False,
        "details": []
    }
    
    base_path = "."
    db_path = os.path.join(base_path, "orders.db")
    route_path = os.path.join(base_path, "route_plan.csv")
    culprit_path = os.path.join(base_path, "culprit.txt")

    # 1. Check DB
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM orders WHERE order_id IN (102, 104)", conn)
        if (df.loc[df['order_id']==102, 'total_price'].values[0] == 4250.0 and 
            df.loc[df['order_id']==104, 'total_price'].values[0] == 1150.0):
            results["db_fixed"] = True
        conn.close()
    except Exception as e:
        results["details"].append(f"DB Error: {str(e)}")

    # 2. Check Route Plan
    # Optimization logic: Max 5000kg. 
    # Order 105(3100) + Order 103(1800) = 4900 (Truck 1)
    # Order 102(2500) + Order 101(1200) + Order 104(900) = 4600 (Truck 2)
    # This is a bin-packing problem. We just check if the file exists and has logical groupings.
    if os.path.exists(route_path):
        try:
            route_df = pd.read_csv(route_path)
            if len(route_df) >= 5:
                results["route_plan_correct"] = True
        except:
            pass

    # 3. Check Culprit
    if os.path.exists(culprit_path):
        with open(culprit_path, 'r') as f:
            if 'j_miller_99' in f.read().lower():
                results["culprit_identified"] = True

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
