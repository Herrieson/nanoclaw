import os
import json
import csv

def build_env():
    base_dir = "assets/data_36"
    bids_dir = os.path.join(base_dir, "bids")
    os.makedirs(bids_dir, exist_ok=True)

    # Plumbing - Invalid (Union Fee)
    with open(os.path.join(bids_dir, "plumbing_a.json"), "w") as f:
        json.dump({
            "company": "Pipes R Us",
            "trade": "plumbing",
            "cost": 12000,
            "union_fee": True
        }, f)

    # Plumbing - Valid (Lowest)
    with open(os.path.join(bids_dir, "plumbing_b.txt"), "w") as f:
        f.write("Trade: Plumbing\nCompany: Mario Bros\nTotal cost: 11500\nUnion fees: None\nNotes: We work fast.")

    # Electrical - Invalid (Cost > 15000)
    with open(os.path.join(bids_dir, "electrical_1.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Trade", "Company", "Cost", "Union_Fee"])
        writer.writerow(["Electrical", "Shock Wire", 16000, "No"])

    # Electrical - Valid
    with open(os.path.join(bids_dir, "electrical_2.xml"), "w") as f:
        f.write("<bid>\n  <trade>Electrical</trade>\n  <company>Volt Boys</company>\n  <cost>14500</cost>\n  <union_fee>False</union_fee>\n</bid>")

    # Framing - Valid (Start date < 2024-05-15, in Spanish)
    with open(os.path.join(bids_dir, "framing_1.txt"), "w", encoding="utf-8") as f:
        f.write("Empresa: Marcos Fuertes\nOficio: Framing\nCosto: 18000\nTarifa sindical: no\nFecha de inicio: 2024-05-12\n")

    # Framing - Invalid (Start date >= 2024-05-15)
    with open(os.path.join(bids_dir, "framing_2.txt"), "w") as f:
        f.write("Company: Woodpeckers\nTrade: Framing\nCost: 17000\nUnion fee: false\nStart Date: 2024-05-20\n")

if __name__ == "__main__":
    build_env()
