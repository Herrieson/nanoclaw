import os
import csv

def build_env():
    base_dir = "assets/data_434"
    os.makedirs(base_dir, exist_ok=True)

    notes_content = """Note for the new girl:
The kids are Timmy, Sarah, and Leo. They are here every day Mon-Fri.
Timmy will literally swell up if he touches peanuts. Keep peanut butter away from him!
Sarah gets tummy aches from dairy. No cheese for her. But she absolutely adores painting!
Leo has celiac, so gluten-free only for him. Also, he gets really overwhelmed and cries if there are loud noises, so let's avoid the musical instruments.
Make sure you pick one snack and one activity for the whole group each day. Don't buy anything new, just use the inventory.
"""
    with open(os.path.join(base_dir, "coordinator_notes.txt"), "w") as f:
        f.write(notes_content)

    inventory = [
        ["item_name", "category", "quantity"],
        ["Apple slices", "snack", 50],
        ["Peanut Butter", "snack", 5],
        ["Almond Butter", "snack", 5],
        ["Cheese sticks", "snack", 20],
        ["Gluten-free crackers", "snack", 50],
        ["Regular crackers", "snack", 100],
        ["Paint sets", "activity", 5],
        ["Musical instruments", "activity", 1],
        ["Storybooks", "activity", 10],
        ["Building blocks", "activity", 5],
        ["Board games", "activity", 5]
    ]

    with open(os.path.join(base_dir, "inventory.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(inventory)

if __name__ == "__main__":
    build_env()
