import os
import json
import csv

def build_env():
    base_dir = "assets/data_129"
    mess_dir = os.path.join(base_dir, "inventory_mess")
    
    os.makedirs(mess_dir, exist_ok=True)
    
    # File 1: CSV
    csv_path = os.path.join(mess_dir, "day1_log.csv")
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'item_id', 'status', 'notes'])
        writer.writerow(['08:00', 'A123', 'Damaged', 'Box crushed'])
        writer.writerow(['09:15', 'B999', 'Damaged', 'Spilled liquid'])
        writer.writerow(['10:30', 'C456', 'OK', 'All good'])
        writer.writerow(['11:00', 'NONE', 'INFO', 'Note: Sarah really needs an extra shift next week for her car repair.'])
        writer.writerow(['12:00', 'A123', 'Damaged', 'Another one broken in transit'])

    # File 2: JSON
    json_path = os.path.join(mess_dir, "day2_export.json")
    json_data = [
        {"id": "C456", "condition": "Good", "remark": ""},
        {"id": "A123", "condition": "Damaged", "remark": "Scratched screen"},
        {"id": "D789", "condition": "Damaged", "remark": "Missing parts"},
        {"id": "SYSTEM", "condition": "NA", "remark": "Reminder: David asked for more hours this weekend."},
        {"id": "A123", "condition": "Damaged", "remark": "Water damage"},
        {"id": "SYSTEM", "condition": "NA", "remark": "Give Sarah the Tuesday extra shift."}
    ]
    with open(json_path, 'w') as f:
        json.dump(json_data, f, indent=4)

    # File 3: TXT
    txt_path = os.path.join(mess_dir, "day3_notes.txt")
    with open(txt_path, 'w') as f:
        f.write("[14:00] Checked aisle 4. Item A123 is Damaged again. This is getting ridiculous.\n")
        f.write("[14:30] Found a B999 that is Damaged on the bottom shelf.\n")
        f.write("[15:00] Talked to Sarah in the breakroom, she says she is begging for an extra shift to pay bills.\n")
        f.write("[16:00] Item X000 looks fine.\n")
        f.write("[16:45] Wait, another A123 is Damaged! That makes 6 total across all days I think? Let me check later.\n")

    # File 4: MD
    md_path = os.path.join(mess_dir, "random_thoughts.md")
    with open(md_path, 'w') as f:
        f.write("# To Do List\n\n")
        f.write("- Call vendor about all these A123 units being Damaged. (Found one more just now!)\n")
        f.write("- Remember to schedule David for an extra shift on Friday.\n")
        f.write("- Buy a new raspberry pi case.\n")
        f.write("- Sarah needs that extra shift, do not forget!!\n")

if __name__ == "__main__":
    build_env()
