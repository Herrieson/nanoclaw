import os
import json
import csv

def build_env():
    # Create the state directory
    state_directory = {
        "PA-101": {"name": "Alice Smith", "dept": "HR-Core"},
        "PA-202": {"name": "Robert Chen", "dept": "IT-Support"},
        "PA-303": {"name": "Maria Garcia", "dept": "Exec-Admin"},
        "PA-404": {"name": "James Wilson", "dept": "Finance"},
        "PA-505": {"name": "Linda Taylor", "dept": "HR-Core"}
    }
    
    with open("state_directory.json", "w") as f:
        json.dump(state_directory, f, indent=4)

    # Create messy visitor logs
    os.makedirs("visitor_logs", exist_ok=True)
    
    # Log 1: CSV format
    with open("visitor_logs/morning_session.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Name_Entered"])
        writer.writerow(["PA-101", "Alice Smith"])
        writer.writerow(["PA-999", "Greggory House"]) # Unauthorized
        writer.writerow(["PA-303", "Maria G."])

    # Log 2: Messy text format
    with open("visitor_logs/afternoon_notes.txt", "w") as f:
        f.write("Attendees for the afternoon:\n")
        f.write("- Robert Chen (ID: PA-202) was there early.\n")
        f.write("- Also someone named 'Chad Bro' signed in with ID PA-888. Weird.\n")
        f.write("- Linda Taylor (PA-505) asked about the recipes.\n")

if __name__ == "__main__":
    build_env()
