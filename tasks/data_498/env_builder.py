import os
import csv

def build_env():
    base_dir = "assets/data_498"
    reg_dir = os.path.join(base_dir, "registrations")
    
    os.makedirs(reg_dir, exist_ok=True)
    
    # 1. CSV Data
    csv_path = os.path.join(reg_dir, "north_district.csv")
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["SchoolName", "Participants", "AmountCollected"])
        writer.writerow(["Lincoln High", "120", "450.50"])
        writer.writerow(["Washington Middle", "85", "200.00"])
        writer.writerow(["Jefferson Elem", "150", "300.00"])

    # 2. Free Text Data
    txt_path = os.path.join(reg_dir, "south_district_email.txt")
    with open(txt_path, 'w') as f:
        f.write("Hey team, here are the final numbers for the South side after my morning run:\n")
        f.write("Oakridge Academy will bring 40 kids and raised $120.\n")
        f.write("Pinecrest High is joining with 90 students, raised $350.5.\n")
        f.write("Maple Leaf Elem: 60 participants, 180 dollars.\n")
        f.write("Thanks!\n")

    # 3. Dropouts
    dropout_path = os.path.join(base_dir, "dropouts.txt")
    with open(dropout_path, 'w') as f:
        f.write("Washington Middle\n")
        f.write("Pinecrest High\n")

if __name__ == "__main__":
    build_env()
