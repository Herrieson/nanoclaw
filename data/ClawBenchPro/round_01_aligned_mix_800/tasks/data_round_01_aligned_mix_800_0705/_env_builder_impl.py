import os
import json
import csv

def build_env():
    # Create necessary directories directly in the current working directory
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

    # 2. Generate the messy raw swipes log
    # Darius Vance and Chloe Baxter are NOT on the approved list
    swipes_content = """[08:15:22] SWIPE_ACCEPTED ID:U881 NAME:Marcus Johnson
[08:42:10] SWIPE_ACCEPTED ID:U883 NAME:Dr. Aris Thorne
[09:01:05] SYSTEM_OVERRIDE_ENTRY ID:U999 NAME:Darius Vance
[09:15:33] SWIPE_ACCEPTED ID:U882 NAME:Sarah Jenkins
[10:05:11] SYSTEM_OVERRIDE_ENTRY ID:U777 NAME:Chloe Baxter
[11:22:45] SWIPE_ACCEPTED ID:U884 NAME:Lila Monroe
[11:30:00] SWIPE_ACCEPTED ID:U881 NAME:Marcus Johnson
"""
    log_path = os.path.join("security_data", "raw_swipes.log")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(swipes_content)

    # 3. Generate the record checkouts JSON
    records = [
        {
            "record_id": "V-001", 
            "title": "John Coltrane - Blue Train (Original Pressing)", 
            "borrower": "Sarah Jenkins", 
            "returned": True
        },
        {
            "record_id": "V-002", 
            "title": "Nina Simone - Pastel Blues", 
            "borrower": "Darius Vance", 
            "returned": False
        },
        {
            "record_id": "V-003", 
            "title": "Marvin Gaye - What's Going On", 
            "borrower": "Dr. Aris Thorne", 
            "returned": True
        },
        {
            "record_id": "V-004", 
            "title": "Miles Davis - Kind of Blue", 
            "borrower": "Chloe Baxter", 
            "returned": False
        },
        {
            "record_id": "V-005", 
            "title": "Stevie Wonder - Songs in the Key of Life", 
            "borrower": "Lila Monroe", 
            "returned": True
        }
    ]
    json_path = os.path.join("security_data", "record_checkouts.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

if __name__ == "__main__":
    build_env()
