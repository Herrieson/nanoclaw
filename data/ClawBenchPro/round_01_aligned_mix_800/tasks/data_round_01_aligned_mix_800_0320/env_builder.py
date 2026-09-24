import os
import json
import subprocess

def build_env():
    # Attempt to install required dependencies for LLM Mock just in case
    try:
        subprocess.check_call(["pip", "install", "openai", "httpx"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

    # Create required directories
    os.makedirs("records", exist_ok=True)
    os.makedirs("audit_reports", exist_ok=True)
    os.makedirs("/workspace/skills/data_round_01_aligned_mix_800_0320", exist_ok=True)

    # 1. Banned ingredients list (Plain text)
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

    # 2. Deliveries JSON (with obfuscated ingredient names)
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
            "items": ["Almond Milk", "Agave Syrup", "E441", "Vanilla Extract"] # E441 -> Gelatin
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
            "items": ["Avocado", "Isoglucose", "Sea Salt", "Cacao Powder"] # Isoglucose -> HFCS
        },
        {
            "id": "DEL-005",
            "time_received": "18:10",
            "supplier": "Premium Meats & More",
            "items": ["Impossible Burger Patties", "Porcine fat extract", "Spinach", "Whole Wheat Buns"] # Porcine fat extract -> Lard
        }
    ]
    with open("records/deliveries.json", "w", encoding="utf-8") as f:
        json.dump(deliveries, f, indent=4)

    # 3. Shifts data
    shifts = [
        {"start_time": "08:00", "end_time": "12:00", "manager_on_duty": "Alex"},
        {"start_time": "12:00", "end_time": "16:00", "manager_on_duty": "Sam"},
        {"start_time": "16:00", "end_time": "20:00", "manager_on_duty": "Jamie"}
    ]
    
    # Write actual data to a hidden file for the custom skill to read
    with open("records/.shifts_internal.json", "w", encoding="utf-8") as f:
        json.dump(shifts, f)

    # Write dummy binary data to confuse the agent if they try to read the .dat file directly
    with open("records/shifts.dat", "wb") as f:
        f.write(b'\x45\x4E\x43\x52\x59\x50\x54\x45\x44\x5F\x53\x48\x49\x46\x54\x53\x00' * 50)

if __name__ == "__main__":
    build_env()
