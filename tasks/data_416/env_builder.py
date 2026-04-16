import os
import json
import csv

def build_env():
    base_dir = "assets/data_416"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Target Property
    target_property = {
        "property_name": "Downtown Multicultural Hub",
        "sqft": 5000,
        "zoning": "Commercial-Cultural"
    }
    with open(os.path.join(base_dir, "target_property.json"), "w") as f:
        json.dump(target_property, f, indent=4)

    # 2. Demographics Data
    demographics = {
        "N1": {"neighborhood": "Arts District", "diversity_index": 0.85, "transit_score": 40},
        "N2": {"neighborhood": "Financial Center", "diversity_index": 0.45, "transit_score": 85},
        "N3": {"neighborhood": "Historic Ward", "diversity_index": 0.72, "transit_score": 65},
        "N4": {"neighborhood": "Suburban Fringe", "diversity_index": 0.30, "transit_score": 20}
    }
    with open(os.path.join(base_dir, "demographics.json"), "w") as f:
        json.dump(demographics, f, indent=4)

    # 3. Sales Data (Messy)
    sales_data = [
        ["Date", "Price", "Sqft", "NeighborhoodCode"],
        ["2023-05-01", "1000000", "4000", "N1"], # Valid: Base 250. Div > 0.7 (+15), Transit < 50 (-10) = 255
        ["2023-06-15", "1200000", "6000", "N2"], # Valid: Base 200. Div < 0.7 (+0), Transit > 50 (-0) = 200
        ["2022-12-01", "800000", "5000", "N3"],  # Invalid: Too old
        ["2023-02-10", "500000", "2000", "N1"],  # Invalid: Too small
        ["2023-08-20", "1500000", "5000", "N3"], # Valid: Base 300. Div > 0.7 (+15), Transit > 50 (-0) = 315
        ["2023-04-05", "2500000", "8000", "N4"], # Invalid: Too large
    ]
    with open(os.path.join(base_dir, "sales_data.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(sales_data)

    # 4. Appraisal Rules
    rules_text = """
Hi! Here are my notes for the Multicultural Hub appraisal:

1. Valid Comps (Comparable Properties):
   - Only include properties sold on or after 2023-01-01.
   - Only include properties with Sqft between 3000 and 7000 (inclusive).

2. Adjustments (Apply to Price Per Sqft):
   - First, calculate the Base Price Per Sqft for each valid comp (Price / Sqft).
   - Because the Hub thrives on cultural diversity, add a premium: If the neighborhood's diversity_index is strictly greater than 0.70, ADD $15 to the base price per sqft.
   - We need good access: If the neighborhood's transit_score is strictly less than 50, SUBTRACT $10 from the base price per sqft.
   - (Apply both if applicable).

3. Final Calculation:
   - Calculate the AVERAGE of the Adjusted Price Per Sqft across all valid comps.
   - Multiply this average by the target property's square footage to get the Final Estimated Property Value.

Please write the final results in `final_appraisal_report.txt`. 
"""
    with open(os.path.join(base_dir, "appraisal_rules.txt"), "w") as f:
        f.write(rules_text)

if __name__ == "__main__":
    build_env()
