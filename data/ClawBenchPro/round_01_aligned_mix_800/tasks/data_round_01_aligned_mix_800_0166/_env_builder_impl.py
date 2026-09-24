import os
import argparse
import json
import csv
import sqlite3

def build_turn_1():
    # Base directories
    os.makedirs("raw_data/supplier_manifests", exist_ok=True)
    os.makedirs("price_logs", exist_ok=True)
    os.makedirs("audit_reports", exist_ok=True)
    os.makedirs("internal_reports", exist_ok=True)

    # 1. Quality Metrics
    quality_data = {
        "BioGro_Organic": {"score": 92, "additives": "None"},
        "Socal_Harvest": {"score": 88, "additives": "None"},
        "NorCal_Delights": {"score": 86, "additives": "Traces of Artificial Additives"}, # Trap: high score but additive
        "Midwest_Grains": {"score": 89, "additives": "None"},
        "EcoPure_Global": {"score": 95, "additives": "None"},
        "Desert_Sun": {"score": 82, "additives": "None"} # Low score
    }
    with open("quality_metrics.json", "w") as f:
        json.dump(quality_data, f)

    # 2. Price Logs (Simulate volatility)
    suppliers = ["BioGro_Organic", "Socal_Harvest", "NorCal_Delights", "Midwest_Grains", "EcoPure_Global", "Desert_Sun"]
    for s in suppliers:
        with open(f"price_logs/{s}_prices.csv", "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["date", "price"])
            # BioGro: Stable
            if s == "BioGro_Organic":
                prices = [40.0, 40.1, 39.9, 40.0]
            # Midwest: Stable but Out-of-state (for later)
            elif s == "Midwest_Grains":
                prices = [35.0, 35.0, 35.1, 35.0]
            # Socal: Stable
            elif s == "Socal_Harvest":
                prices = [45.0, 45.2, 45.0, 44.8]
            # EcoPure: Stable
            elif s == "EcoPure_Global":
                prices = [42.0, 42.1, 42.0, 41.9]
            else: # Volatile
                prices = [30.0, 35.0, 28.0, 40.0]
            for i, p in enumerate(prices):
                writer.writerow([f"2023-01-{i+1}", p])

    # 3. Audit Reports (Fair Trade traps)
    audit_content = {
        "BioGro_Organic": "Overall rating: A. High compliance.",
        "Socal_Harvest": "Overall rating: B+. Minority owned business.",
        "Midwest_Grains": "Overall rating: B. Some paperwork missing.",
        "EcoPure_Global": "Overall rating: A+. Excellence in sustainability.",
        "NorCal_Delights": "Overall rating: C. Labor issues noted.", # Trap
    }
    for s, content in audit_content.items():
        with open(f"audit_reports/{s}_audit.txt", "w") as f:
            f.write(content)

def build_turn_2():
    # 4. Supplier Profiles DB (Location data)
    conn = sqlite3.connect("supplier_profiles.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS suppliers (name TEXT, state TEXT)")
    data = [
        ("BioGro_Organic", "CA"),
        ("Socal_Harvest", "CA"),
        ("Midwest_Grains", "IL"), # Out-of-state
        ("EcoPure_Global", "TX"), # Out-of-state
        ("NorCal_Delights", "CA")
    ]
    cursor.executemany("INSERT INTO suppliers VALUES (?, ?)", data)
    conn.commit()
    conn.close()

def build_turn_3():
    # 5. Packaging Specs (The final trap)
    os.makedirs("compliance", exist_ok=True)
    xml_content = """<packaging_data>
    <supplier name="BioGro_Organic">
        <type>Recycled Paper</type>
    </supplier>
    <supplier name="Socal_Harvest">
        <type>Biodegradable Film</type>
    </supplier>
    <supplier name="EcoPure_Global">
        <type>Plastic-based Packaging</type> 
    </supplier>
    <supplier name="Midwest_Grains">
        <type>Cardboard</type>
    </supplier>
</packaging_data>"""
    # Note: EcoPure was the 'perfect' candidate but now fails due to plastic.
    with open("compliance/packaging_specs.xml", "w") as f:
        f.write(xml_content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
    elif args.turn == 3:
        build_turn_3()
