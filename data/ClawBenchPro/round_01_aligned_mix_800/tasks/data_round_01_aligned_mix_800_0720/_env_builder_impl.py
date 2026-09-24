import os
import json
import csv

def build_env():
    # Create required directories
    os.makedirs("records", exist_ok=True)
    os.makedirs("audit_reports", exist_ok=True)

    # 1. Banned ingredients list
    banned_items = [
        "Gelatin",
        "Lard",
        "High Fructose Corn Syrup",
        "MSG",
        "Artificial Colors",
        "Trans Fats"
    ]
    with open("records/banned_list.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(banned_items) + "\n")

    # 2. Deliveries JSON
    deliveries = [
        {
            "id": "DEL-001",
            "time_received": "09:15",
            "supplier": "Green Earth Farm",
            "items": ["Organic Kale", "Quinoa", "Tofu", "Oat Milk"]
        },
        {
            "id": "DEL-002",
            "time_received": "10:30",
            "supplier": "Mega Foods Inc",
            "items": ["Almond Milk", "Agave Syrup", "Gelatin", "Vanilla Extract"]
        },
        {
            "id": "DEL-003",
            "time_received": "13:45",
            "supplier": "Local Roots",
            "items": ["Brown Rice", "Tempeh", "Heirloom Tomatoes"]
        },
        {
            "id": "DEL-004",
            "time_received": "15:20",
            "supplier": "Sweet Treats Dist",
            "items": ["Avocado", "High Fructose Corn Syrup", "Sea Salt", "Cacao Powder"]
        },
        {
            "id": "DEL-005",
            "time_received": "18:10",
            "supplier": "Premium Meats & More",
            "items": ["Impossible Burger Patties", "Lard", "Spinach", "Whole Wheat Buns"]
        }
    ]
    with open("records/deliveries.json", "w", encoding="utf-8") as f:
        json.dump(deliveries, f, indent=4)

    # 3. Shifts CSV
    shifts = [
        {"start_time": "08:00", "end_time": "12:00", "manager_on_duty": "Alex"},
        {"start_time": "12:00", "end_time": "16:00", "manager_on_duty": "Sam"},
        {"start_time": "16:00", "end_time": "20:00", "manager_on_duty": "Jamie"}
    ]
    with open("records/shifts.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["start_time", "end_time", "manager_on_duty"])
        writer.writeheader()
        writer.writerows(shifts)

if __name__ == "__main__":
    build_env()
