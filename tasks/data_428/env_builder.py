import os
import csv

def build_env():
    base_dir = "assets/data_428"
    os.makedirs(base_dir, exist_ok=True)

    csv_path = os.path.join(base_dir, "factory_shipments.csv")
    csv_data = [
        ["batch_id", "item_type", "quantity", "destination"],
        ["B001", "WearableTech", "100", "Ohio"],
        ["B002", "BasicApparel", "50", "Ohio"],
        ["B003", "WearableTech", "200", "NewYork"],
        ["B004", "WearableTech", "80", "Ohio"],
        ["B005", "WearableTech", "150", "California"],
        ["B006", "BasicApparel", "300", "Ohio"]
    ]
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

    log_path = os.path.join(base_dir, "system_sync.log")
    log_data = """[2023-10-27 01:22:10] INFO - System sync started.
[2023-10-27 01:25:33] WARN - QA failed for B001. 12 units damaged and removed from inventory.
[2023-10-27 01:30:00] UPDATE - Logistics route changed due to weather. B003 is now heading to Ohio.
[2023-10-27 01:45:12] NOTICE - Retrofit complete. B002 has been upgraded with smart modules. Item type is now WearableTech.
[2023-10-27 01:50:00] INFO - Routine scan for B005 completed successfully.
[2023-10-27 02:00:00] CRITICAL - B004 shipment completely lost in transit fire. Quantity set to 0.
[2023-10-27 02:05:00] INFO - Sync complete. All other batches remain unchanged.
"""
    with open(log_path, 'w') as f:
        f.write(log_data)

if __name__ == "__main__":
    build_env()
