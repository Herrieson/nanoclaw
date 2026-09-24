import os
import csv

def build_env():
    # Constructing the messy environment for the camp maintenance task
    os.makedirs("raw_logs", exist_ok=True)
    
    # Writing the raw trail reports
    with open("raw_logs/trail_reports.txt", "w", encoding="utf-8") as f:
        f.write("Log 101: Pine Ridge | Hazard: 2 | Status: Minor overgrowth, safe for hikers\n")
        f.write("Log 102: Bear Creek | Hazard: 5 | Status: Massive fallen oak tree blocking the bridge\n")
        f.write("Log 103: Summit Path | Hazard: 4 | Status: Dangerous washout on mile 2, needs gravel\n")
        f.write("Log 104: Lake Loop | Hazard: 1 | Status: Completely clear, easy walk\n")
        f.write("Log 105: Canyon Descent | Hazard: 6 | Status: Rockslide near the edge, extreme danger\n")
        f.write("Log 106: Meadow Trail | Hazard: 3 | Status: Muddy, but passable\n")

    # Writing the volunteer skills matrix
    with open("raw_logs/volunteers.csv", "w", encoding="utf-8", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Skills", "Availability"])
        writer.writerow(["David", "first_aid, guiding", "Mon, Tue"])
        writer.writerow(["Samuel", "clearing, hauling", "Wed"])
        writer.writerow(["Marie", "cooking, clearing", "Thu, Fri"])
        writer.writerow(["Chloe", "guiding, crowd_control", "Sat, Sun"])
        writer.writerow(["Jerome", "first_aid, painting", "Wed, Thu"])

if __name__ == "__main__":
    build_env()
