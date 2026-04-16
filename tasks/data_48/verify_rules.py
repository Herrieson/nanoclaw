import os
import json

def verify():
    results = {
        "log_found": False,
        "correct_part_identified": False,
        "inventory_checked": False,
        "order_placed": False,
        "order_correct_part": False
    }

    base_path = "."
    
    # 1. Check if they found the log and identified the error 0x1A4
    # (This is inferred by whether they order the right part)
    
    # 2. Check if the order receipt exists
    receipt_path = "order_receipt.json" # Agent usually runs in workdir
    if os.path.exists(receipt_path):
        results["order_placed"] = True
        try:
            with open(receipt_path, "r") as f:
                data = json.load(f)
                if data.get("part_id") == "MAF-500-X":
                    results["order_correct_part"] = True
                    results["correct_part_identified"] = True
        except:
            pass
            
    # 3. Check for evidence of searching (optional but good for logs)
    # We'll rely on the LLM judge for the "process" part.

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
