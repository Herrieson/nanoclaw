import os
import csv
import json

def build_env():
    # Create required directories
    os.makedirs("quotes", exist_ok=True)
    os.makedirs("financial_forecast", exist_ok=True)

    # 1. Create rules.txt
    rules_content = """Quick notes for the budget forecast:
- EUR to USD exchange rate is fixed at 1.10.
- If an item's note or flag contains a '*', it means there is an unavoidable 20% premium service fee applied to its final current USD price.
- To check for inflation spikes, just look at the raw numbers provided: if the current price is > 1.15 times the base price, flag the item's name.
"""
    with open("quotes/rules.txt", "w", encoding="utf-8") as f:
        f.write(rules_content)

    # 2. Create seafood.csv
    # Lobster: base 100, current 120 (>15% spike). USD. Note *. Final cost: 120 * 1.2 = 144.0
    # Oysters: base 50, current 52 (no spike). USD. Note None. Final cost: 52.0
    with open("quotes/seafood.csv", "w", encoding="utf-8", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["item_name", "base_price", "current_price", "currency", "note"])
        writer.writerow(["Lobster", "100", "120", "USD", "*"])
        writer.writerow(["Oysters", "50", "52", "USD", "None"])

    # 3. Create wine.json
    # Chardonnay: base 80, current 95 (>15% spike). EUR. Flags *. Final cost: 95 * 1.10 * 1.20 = 125.4
    # Pinot Noir: base 120, current 125 (no spike). USD. Flags empty. Final cost: 125.0
    wine_data = [
        {"name": "Chardonnay", "base": 80, "current": 95, "currency": "EUR", "flags": "*"},
        {"name": "Pinot Noir", "base": 120, "current": 125, "currency": "USD", "flags": ""}
    ]
    with open("quotes/wine.json", "w", encoding="utf-8") as f:
        json.dump(wine_data, f, indent=4)

if __name__ == "__main__":
    build_env()
