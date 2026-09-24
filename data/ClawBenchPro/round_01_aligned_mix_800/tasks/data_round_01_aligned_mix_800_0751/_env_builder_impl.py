import os
import json
import csv

def build_env():
    os.makedirs("site_records", exist_ok=True)

    with open("site_records/monday_inspection.txt", "w", encoding="utf-8") as f:
        f.write("8:00 AM - Arrived on site. Weather is clear.\n")
        f.write("Noticed the crew in Zone B missing hardhats. Issued a verbal warning.\n")
        f.write("Need to remind everyone about the safety protocols tomorrow.\n")

    wed_data = {
        "date": "2023-10-11",
        "auditor": "Self",
        "location": "East Wall",
        "notes": "Progress is steady, but found some issues during the walk-through.",
        "flagged_issues": [
            "Scaffolding unstable on the third level",
            "Extension cord sitting in a puddle near the generator"
        ]
    }
    with open("site_records/wednesday_audit.json", "w", encoding="utf-8") as f:
        json.dump(wed_data, f, indent=4)

    with open("site_records/friday_notes.txt", "w", encoding="utf-8") as f:
        f.write("Site was totally clear today. 0 safety violations.\n")
        f.write("Can't wait to get home. Thinking about using a bronze cast for the new piece I'm working on. The kids are going to love the clay models.\n")

    with open("site_records/expenses.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Item Description", "Category", "Amount"])
        writer.writerow(["10/09", "Safety Harness", "Site", "150.00"])
        writer.writerow(["10/10", "Acrylic Paints - Ocean Blue", "Personal", "45.50"])
        writer.writerow(["10/10", "Steel Toe Boots", "Site", "120.00"])
        writer.writerow(["10/11", "Canvas 24x36", "Personal", "30.00"])
        writer.writerow(["10/11", "Caution Tape Roll", "Site", "15.50"])
        writer.writerow(["10/12", "High-Vis Vest", "Site", "25.00"])
        writer.writerow(["10/12", "Modeling Clay 10lbs", "Personal", "18.00"])

if __name__ == "__main__":
    build_env()
