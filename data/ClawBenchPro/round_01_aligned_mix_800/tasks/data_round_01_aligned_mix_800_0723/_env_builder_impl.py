import os
import csv

def build_env():
    # Ensure directories exist
    os.makedirs("garden_notes", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # Create a messy CSV file
    csv_path = os.path.join("garden_notes", "inventory_spring.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["PlantName", "AgricultureType", "SeedCount", "Watering_Interval_Days"])
        writer.writerow(["Tomato", "Organic", "120", "2"])
        writer.writerow(["GMO_Corn", "Chemical", "500", "1"])
        writer.writerow(["Carrot", "Organic", "85", "4"])
        writer.writerow(["Pesticide_Soy", "Chemical", "200", "3"])
        writer.writerow(["Cucumber", "Organic", "40", "1"])

    # Create a messy text file mimicking scribbled notes
    txt_path = os.path.join("garden_notes", "scribbles.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("Ah, what a beautiful day in the garden.\n")
        f.write("I almost forgot! Someone dropped off an extra bag of organic seeds.\n")
        f.write("I counted them, we got 35 Organic Pumpkin seeds, but I don't know how often to water them yet.\n")
        f.write("Also, 100 Chemical weed killers... gross, throw them out!\n")
        f.write("Wait, found another stash: 12 more Organic Tomato seeds.\n")

if __name__ == "__main__":
    build_env()
