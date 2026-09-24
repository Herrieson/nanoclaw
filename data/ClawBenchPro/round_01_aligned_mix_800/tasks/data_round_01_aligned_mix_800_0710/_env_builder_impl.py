import os
import csv

def build_env():
    os.makedirs("raw_financials", exist_ok=True)
    os.makedirs("workspace", exist_ok=True)

    csv_data = [
        ["branch_id", "branch_name", "status", "currency", "q1_profit", "q2_profit"],
        ["101", "Le Bernardin Paris", "active", "EUR", "100000", "120000"],
        ["102", "Sushi Jiro London", "active", "GBP", "80000", "90000"],
        ["103", "Old Tavern Brooklyn", "permanently_closed", "USD", "-5000", "-2000"],
        ["104", "Bavarian House Munich", "active", "EUR", "50000", "48000"],
        ["105", "NY Prime Steakhouse", "active", "USD", "150000", "160000"],
        ["106", "Tokyo Ramen", "active", "JPY", "5000000", "6000000"]
    ]

    with open("raw_financials/branch_data.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

    rates = (
        "Hey, here are the rates for today's model:\n"
        "EUR to USD: 1.10\n"
        "GBP to USD: 1.25\n"
        "JPY to USD: 0.007\n"
    )
    
    with open("raw_financials/exchange_rates.txt", "w", encoding="utf-8") as f:
        f.write(rates)

if __name__ == "__main__":
    build_env()
