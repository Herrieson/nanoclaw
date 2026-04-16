import os

def build_env():
    base_dir = "assets/data_98/wood_projects"
    os.makedirs(base_dir, exist_ok=True)

    picnic_csv = """Part,Material,Length_in_inches,Qty
Top,2x4,72,6
Seat,2x4,72,4
Leg,4x4,36,4
Brace,2x4,30,2
"""
    with open(os.path.join(base_dir, "picnic_table.csv"), "w") as f:
        f.write(picnic_csv)

    chairs_txt = """Chair cut list (per chair, need 2 chairs total):
Legs: 4x4, 2 feet long, 4 pieces.
Seat: 2x4, 24 inches long, 6 pieces.
Back: 2x4, 30 inches long, 3 pieces.
"""
    with open(os.path.join(base_dir, "chairs.txt"), "w") as f:
        f.write(chairs_txt)

    notes_log = """Tuesday: Downloaded picnic table plans. Looks good.
Wednesday: Got the chair plans.
Thursday: Actually, scratch the chairs. The wife says they take up too much space. Ignore the chairs.txt file entirely!
Instead, I'll build a small side table.
Side table cuts:
- 4 legs made of 4x4. Each needs to be 18 inches long.
- 6 top slats made of 2x4. Each 24 inches long.

Need to sum everything up before I hit the road.
"""
    with open(os.path.join(base_dir, "notes.log"), "w") as f:
        f.write(notes_log)

if __name__ == "__main__":
    build_env()
