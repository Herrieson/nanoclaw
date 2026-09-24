import sys
import json
import os

def run(sku_input):
    """
    Look up SKU IDs in the master inventory list.
    """
    master_list_path = "metadata/sku_master_list.json"
    if not os.path.exists(master_list_path):
        return "Error: Master SKU database not found."

    with open(master_list_path, "r") as f:
        master_data = json.load(f)

    if isinstance(sku_input, str):
        skus = [sku_input]
    else:
        skus = sku_input

    results = {}
    for sku in skus:
        results[sku] = master_data.get(sku, "UNKNOWN_ITEM")
    
    return json.dumps(results)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(run(sys.argv[1]))
