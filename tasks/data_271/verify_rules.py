import os
import pandas as pd
import json

def verify():
    base_path = "project_files"
    target_file = os.path.join(base_path, "weekly_balance_final.csv")
    results = {
        "file_exists": False,
        "correct_rows": 0,
        "ghost_stock_filtered": False,
        "discrepancy_correct": False
    }

    if os.path.exists(target_file):
        results["file_exists"] = True
        try:
            df = pd.read_csv(target_file)
            results["correct_rows"] = len(df)
            
            # 校验 SKU005 是否被作为 ghost_stock 过滤掉 (Log 中的线索)
            if "SKU005" not in df['sku'].values:
                results["ghost_stock_filtered"] = True
            
            # 校验 SKU001 的差异是否正确 (150 - 148 = 2)
            sku001_diff = df[df['sku'] == 'SKU001']['discrepancy'].iloc[0]
            if int(sku001_diff) == 2:
                results["discrepancy_correct"] = True
        except Exception as e:
            results["error"] = str(e)

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
