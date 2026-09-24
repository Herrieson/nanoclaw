import os
import csv
import subprocess
import sys

def build_env():
    # Install dependencies required by the LLM-as-a-Mock skills
    print("Installing requirements for mock skills...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "openai", "httpx"])

    os.makedirs("inventory_scans", exist_ok=True)
    
    # Dataset 1: Standard aisle scans (Now stripped of min_stock and explicit status)
    # Condition codes: 00 = Normal, 99 = Damaged, 44 = Missing Tag
    data1 = [
        ["sku", "quantity", "condition_code"],
        ["SKU-1001", "45", "00"],
        ["SKU-1002", "5", "00"], 
        ["SKU-1003", "2", "99"],  
        ["SKU-1004", "12", "00"], 
    ]
    
    # Dataset 2: Slightly messy data
    data2 = [
        ["sku", "quantity", "condition_code"],
        ["SKU-2001", "8", "00"], 
        ["SKU-2002", "0", "99"], 
        ["SKU-2003", "22", "00"], 
        ["SKU-2004", "10", "44"], 
    ]

    # Dataset 3: Another aisle
    data3 = [
        ["sku", "quantity", "condition_code"],
        ["SKU-3001", "4", "99"], 
        ["SKU-3002", "15", "00"], 
        ["SKU-3003", "2", "00"], 
    ]

    def write_csv(filename, rows):
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(rows)

    write_csv("inventory_scans/aisle_A.csv", data1)
    write_csv("inventory_scans/tech_gadgets_B.csv", data2)
    write_csv("inventory_scans/fitness_C.csv", data3)
    print("Environment built successfully: created stripped scan logs in 'inventory_scans/'.")

if __name__ == "__main__":
    build_env()
