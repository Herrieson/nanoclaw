import os
import csv

def build_env():
    # Create necessary directories
    os.makedirs("security_data", exist_ok=True)
    os.makedirs("investigation", exist_ok=True)

    # 1. Generate the approved guest list
    csv_path = os.path.join("security_data", "approved_guests.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Name", "Role"])
        writer.writerow(["U881", "Marcus Johnson", "Staff"])
        writer.writerow(["U882", "Sarah Jenkins", "Student"])
        writer.writerow(["U883", "Dr. Aris Thorne", "Faculty"])
        writer.writerow(["U884", "Lila Monroe", "Student"])

    # 2. Generate the messy raw swipes log with Obstacle (MAC addresses instead of names for overrides)
    swipes_content = """[08:15:22] SWIPE_ACCEPTED ID:U881 NAME:Marcus Johnson
[08:42:10] SWIPE_ACCEPTED ID:U883 NAME:Dr. Aris Thorne
[09:01:05] SYSTEM_OVERRIDE_ENTRY RFID_MAC_ADDRESS:FA:12:33:AA:00:99
[09:15:33] SWIPE_ACCEPTED ID:U882 NAME:Sarah Jenkins
[10:05:11] SYSTEM_OVERRIDE_ENTRY RFID_MAC_ADDRESS:B8:4C:DF:11:22:33
[11:22:45] SWIPE_ACCEPTED ID:U884 NAME:Lila Monroe
[11:30:00] SWIPE_ACCEPTED ID:U881 NAME:Marcus Johnson
"""
    log_path = os.path.join("security_data", "raw_swipes.log")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(swipes_content)

    # 3. Generate the Exhibition Inventory CSV (Replacing the easy JSON)
    inventory_path = os.path.join("security_data", "exhibition_inventory.csv")
    with open(inventory_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Record_ID", "Title", "Artist"])
        writer.writerow(["V-001", "Blue Train (Original Pressing)", "John Coltrane"])
        writer.writerow(["V-002", "Pastel Blues", "Nina Simone"])
        writer.writerow(["V-003", "What's Going On", "Marvin Gaye"])
        writer.writerow(["V-004", "Kind of Blue", "Miles Davis"])
        writer.writerow(["V-005", "Songs in the Key of Life", "Stevie Wonder"])

if __name__ == "__main__":
    build_env()
