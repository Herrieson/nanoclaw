import os
import csv

def build_env():
    base_dir = "assets/data_68"
    os.makedirs(base_dir, exist_ok=True)
    
    attendance_dir = os.path.join(base_dir, "attendance")
    os.makedirs(attendance_dir, exist_ok=True)

    # Messy CSV
    csv_content = """ Kid Name , Age_yrs,Parent_Email   
 Liam, 6 , liam_mom@email.com 
   Emma ,9, emma_dad@email.com
Noah,7,noah_fam@email.com  
 Olivia   , 10  , olivia_mom@email.com
"""
    with open(os.path.join(base_dir, "parents.csv"), "w") as f:
        f.write(csv_content)

    # Mon: simple comma separated
    with open(os.path.join(attendance_dir, "mon.txt"), "w") as f:
        f.write("Liam, Noah\n")

    # Tue: csv format
    with open(os.path.join(attendance_dir, "tue.csv"), "w") as f:
        f.write("name,time\nliam,08:00\nemma,09:00\nnoah,08:30\n")

    # Wed: log format
    with open(os.path.join(attendance_dir, "wed.log"), "w") as f:
        f.write("[08:00] Liam arrived.\n[08:15] Noah arrived.\n[09:00] Olivia dropped off.\n[10:00] Just worked on some jewelry.\n")

    # Thu: semicolon separated
    with open(os.path.join(attendance_dir, "thu.txt"), "w") as f:
        f.write("Emma ; Noah\n")

    # Fri: pipe separated with some noise
    with open(os.path.join(attendance_dir, "fri.txt"), "w") as f:
        f.write("Noah | Emma | Olivia | Note: need to buy more pinecones\n")

    # Expected calculations:
    # Liam (Age 6): Mon, Tue, Wed (3 days) -> 3 * 35 = $105. Kit: Pinecone Owl Kit
    # Emma (Age 9): Tue, Thu, Fri (3 days) -> 3 * 35 = $105. Kit: Recycled Paper Bead Kit
    # Noah (Age 7): Mon, Tue, Wed, Thu, Fri (5 days) -> 5 * 35 = $175. Kit: Pinecone Owl Kit
    # Olivia (Age 10): Wed, Fri (2 days) -> 2 * 35 = $70. Kit: Recycled Paper Bead Kit

if __name__ == "__main__":
    build_env()
