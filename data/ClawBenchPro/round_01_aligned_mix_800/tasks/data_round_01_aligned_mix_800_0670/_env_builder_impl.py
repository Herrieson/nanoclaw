import os
import csv

def build_env():
    # Create directories for the workspace
    os.makedirs("pantry_records", exist_ok=True)
    
    # Generate CSV record with a mix of valid and invalid items
    with open("pantry_records/box1.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["item_name", "quantity", "notes"])
        writer.writerow(["Canned Beans", "30", "good condition"])
        writer.writerow(["Canned Beans", "20", "fresh"])
        writer.writerow(["Bread", "10", "expired"])
        writer.writerow(["Blankets", "5", "blessed by pastor"])
        
    # Generate an unstructured TXT record
    with open("pantry_records/notes.txt", "w", encoding="utf-8") as f:
        f.write("Brother Thomas dropped off some items today:\n")
        f.write("- 10 Blankets (freshly washed)\n")
        f.write("- 20 Canned Soup (looks good)\n")
        f.write("- 5 Milk (smells spoiled, do not use)\n")
        
    # Generate the requested needs CSV
    with open("congregation_needs.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["family_id", "requests"])
        writer.writerow(["F-01", "Canned Beans: 15, Blankets: 4"])
        writer.writerow(["F-02", "Canned Soup: 25, Bread: 5"])
        writer.writerow(["F-03", "Canned Beans: 40, Milk: 2"])

if __name__ == "__main__":
    build_env()
