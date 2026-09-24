import os
import json
import csv

def build_env():
    os.makedirs("sales_data", exist_ok=True)
    os.makedirs("compliance_forms", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    
    # Asset catalog
    catalog = {
        "EQ-881": {"name": "Solar Industrial Pump", "category": "Green"},
        "EQ-902": {"name": "Diesel Generator HD", "category": "Standard"},
        "EQ-334": {"name": "Wind Turbine Portable", "category": "Green"},
        "EQ-100": {"name": "Standard Steel Scaffolding", "category": "Standard"}
    }
    with open("catalog.json", "w") as f:
        json.dump(catalog, f, indent=2)
        
    # Sales data logs
    sales = [
        {"contract_id": "CTX-001", "rep": "Carlos", "asset_id": "EQ-881"},
        {"contract_id": "CTX-002", "rep": "Carlos", "asset_id": "EQ-902"},
        {"contract_id": "CTX-003", "rep": "Carlos", "asset_id": "EQ-334"}, 
        {"contract_id": "CTX-004", "rep": "Sarah", "asset_id": "EQ-100"},  
        {"contract_id": "CTX-005", "rep": "Sarah", "asset_id": "EQ-334"},  
        {"contract_id": "CTX-006", "rep": "Sarah", "asset_id": "EQ-881"}   
    ]
    
    with open("sales_data/august_sales.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["contract_id", "rep", "asset_id"])
        writer.writeheader()
        writer.writerows(sales)
        
    # Compliance forms (Intentionally missing CTX-003 for a Green asset)
    forms = ["CTX-001", "CTX-005", "CTX-006"]
    for c in forms:
        with open(f"compliance_forms/{c}_signed.txt", "w") as f:
            f.write("I hereby swear to abide by the environmental regulations.\nSigned by Client.")

if __name__ == "__main__":
    build_env()
