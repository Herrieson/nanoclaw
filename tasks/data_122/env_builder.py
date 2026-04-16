import os
import json
import csv

def build_env():
    # Target directory
    base_dir = "assets/data_122"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Deliveries Log (Tuesday 2023-10-10)
    deliveries = [
        {
            "delivery_id": "DEL-9920",
            "timestamp": "2023-10-10T09:15:00",
            "vendor": "McKesson",
            "items": {
                "Amoxicillin 500mg": 2000,
                "Lisinopril 10mg": 1500
            }
        },
        {
            "delivery_id": "DEL-9921",
            "timestamp": "2023-10-10T14:35:00",
            "vendor": "CardinalHealth_SchII",
            "items": {
                "Oxycodone 10mg": 500,
                "Adderall 20mg": 300,
                "Ibuprofen 800mg": 1000
            }
        }
    ]
    with open(os.path.join(base_dir, "deliveries.json"), "w") as f:
        json.dump(deliveries, f, indent=4)

    # 2. Vault Counts (Monday 2023-10-09 and Wednesday 2023-10-11)
    # Expected on Wed = Mon count + Deliveries (assuming no dispenses for simplicity of this audit, or rather, this is the raw intake audit vault)
    vault_counts = {
        "2023-10-09_EOD": {
            "Amoxicillin 500mg": 500,
            "Lisinopril 10mg": 200,
            "Oxycodone 10mg": 1000,
            "Adderall 20mg": 500,
            "Ibuprofen 800mg": 2000
        },
        "2023-10-11_SOD": {
            "Amoxicillin 500mg": 2500,  # 500 + 2000 = 2500 (Correct)
            "Lisinopril 10mg": 1700,    # 200 + 1500 = 1700 (Correct)
            "Oxycodone 10mg": 1450,     # 1000 + 500 = 1500 (Short by 50)
            "Adderall 20mg": 750,       # 500 + 300 = 800 (Short by 50)
            "Ibuprofen 800mg": 3000     # 2000 + 1000 = 3000 (Correct)
        }
    }
    with open(os.path.join(base_dir, "vault_counts.json"), "w") as f:
        json.dump(vault_counts, f, indent=4)

    # 3. Punch Cards (Tuesday 2023-10-10)
    # Delivery DEL-9921 arrived at 14:35. 
    # Sarah left at 14:15. John clocked in at 14:00. Mark clocked in at 15:00.
    # Therefore, John Davis is the only one on shift at 14:35.
    punch_cards = [
        {"Date": "2023-10-10", "Employee": "Sarah Jenkins", "ClockIn": "06:00", "ClockOut": "14:15"},
        {"Date": "2023-10-10", "Employee": "John Davis", "ClockIn": "14:00", "ClockOut": "22:00"},
        {"Date": "2023-10-10", "Employee": "Mark Thompson", "ClockIn": "15:00", "ClockOut": "23:00"}
    ]
    with open(os.path.join(base_dir, "punch_cards.csv"), "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Date", "Employee", "ClockIn", "ClockOut"])
        writer.writeheader()
        writer.writerows(punch_cards)

if __name__ == "__main__":
    build_env()
