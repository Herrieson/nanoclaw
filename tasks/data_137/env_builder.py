import os
import csv

def build_env():
    base_dir = "assets/data_137"
    os.makedirs(base_dir, exist_ok=True)

    # Chaotic inventory notes reflecting low conscientiousness and high neuroticism
    notes_content = """Inventory Log - November
Oh god, this month is already so stressful.

11/01: Received 500 units of Bamboo Fiber in [Receiving]. It smells super earthy. 
11/02: Moved 300 units from [Receiving] to [Storage_A]. The forklift almost tipped over, I was holding my breath the whole time!
11/03: Wait, scratch that last entry. I just checked with Dave. Only 200 went to [Storage_A], the other 100 stayed in [Receiving]. I swear nobody tells me anything.
11/04: Transferred 50 units from [Receiving] to [Prep]. Also, I finally nailed my grandmother's recipe for vegan bun bo hue last night!
11/05: Disaster. [Prep] got a water leak and ruined 20 units of the Bamboo Fiber. We had to throw them out. Scrapped completely. My anxiety is through the roof today.
11/06: The floor manager yelled at me so I quickly moved 150 units from [Storage_A] to [Prep].
11/07: Wait, did [Prep] need more? No, I think they're fine. But [Receiving] sent 30 units to [Storage_B] just to clear floor space.
"""
    
    with open(os.path.join(base_dir, "inventory_notes.txt"), "w", encoding="utf-8") as f:
        f.write(notes_content)

    # Production schedule
    schedule_data = [
        ["OrderID", "Material", "RequiredUnits", "Destination"],
        ["990", "Recycled Plastic", "100", "Assembly"],
        ["991", "Hemp Fabric", "150", "Assembly"],
        ["992", "Bamboo Fiber", "240", "Assembly"],
        ["993", "Organic Cotton", "80", "Packaging"]
    ]

    with open(os.path.join(base_dir, "schedule.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(schedule_data)

if __name__ == "__main__":
    build_env()
