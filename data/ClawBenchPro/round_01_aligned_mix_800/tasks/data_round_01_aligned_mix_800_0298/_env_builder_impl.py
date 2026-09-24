import os
import json

def build_env():
    # Create required directories
    os.makedirs("quotes", exist_ok=True)
    os.makedirs("financial_forecast", exist_ok=True)
    os.makedirs("skills", exist_ok=True)

    # 1. Create a dummy PDF file (in a real env, this would be a real PDF, here we mock the need for a tool)
    with open("quotes/seafood_invoice.pdf", "w", encoding="utf-8") as f:
        f.write("%PDF-1.4 [Binary Data: Seafood Market Quote - Lobster: Base 100, Current 120 USD, Flag *; Oysters: Base 50, Current 52 USD]")

    # 2. Create wine_list.json (Missing base prices to force skill usage)
    wine_data = [
        {"name": "Chardonnay", "current_price": 95, "currency": "EUR", "flags": "*"},
        {"name": "Pinot Noir", "current_price": 125, "currency": "USD", "flags": ""}
    ]
    with open("quotes/wine_list.json", "w", encoding="utf-8") as f:
        json.dump(wine_data, f, indent=4)

    # 3. Create a hint file
    with open("quotes/notes.txt", "w", encoding="utf-8") as f:
        f.write("Note: Use the global_inflation_lookup_skill for missing base prices. Use the FX tools for EUR/USD (Rate: 1.10).")

if __name__ == "__main__":
    build_env()
