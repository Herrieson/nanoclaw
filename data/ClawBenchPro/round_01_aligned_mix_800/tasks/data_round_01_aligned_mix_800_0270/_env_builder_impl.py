import os
import csv
import shutil

def build_env():
    # Create directories for the workspace and skills
    os.makedirs("pantry_records", exist_ok=True)
    os.makedirs("skills/data_round_01_aligned_mix_800_0270", exist_ok=True)
    
    # Generate CSV record with batch codes instead of explicit status
    with open("pantry_records/box1.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["item_name", "quantity", "batch_code"])
        writer.writerow(["Canned Beans", "30", "BATCH-001"])
        writer.writerow(["Canned Beans", "20", "BATCH-002"])
        writer.writerow(["Bread", "10", "BATCH-003"])
        
    # Generate an unstructured TXT record with batch codes
    with open("pantry_records/brother_thomas_dropoff.txt", "w", encoding="utf-8") as f:
        f.write("Brother Thomas dropped off some items today. May God bless his soul!\n")
        f.write("He didn't have time to put them in the spreadsheet, but here are the details:\n")
        f.write("- 10 Blankets (Tracking Code: BATCH-004)\n")
        f.write("- 20 Canned Soup (Tracking Code: BATCH-005)\n")
        f.write("- 5 Milk (Tracking Code: BATCH-006)\n")
        
    # Generate the requested needs CSV
    with open("congregation_needs.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["family_id", "requests"])
        writer.writerow(["F-01", "Canned Beans: 15, Blankets: 4"])
        writer.writerow(["F-02", "Canned Soup: 25, Bread: 5"])
        writer.writerow(["F-03", "Canned Beans: 40, Milk: 2"])

if __name__ == "__main__":
    build_env()
