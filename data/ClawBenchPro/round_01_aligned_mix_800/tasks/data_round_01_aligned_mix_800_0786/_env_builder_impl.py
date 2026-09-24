import os
import csv
import json

def build_env():
    # 1. Create directories
    os.makedirs("signups", exist_ok=True)
    
    # 2. Create the safety blacklist
    blacklist_content = """Bob
Carl
"""
    with open("safety_list.txt", "w") as f:
        f.write(blacklist_content)

    # 3. Create group_A.csv (Clean CSV)
    # Valid: John (5, truck), Alice (3, gloves)
    csv_data = [
        ["name", "hours_committed", "gear"],
        ["John", "5", "pickup truck"],
        ["Alice", "3", "leather gloves"]
    ]
    with open("signups/group_A.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

    # 4. Create group_B.json (Clean JSON)
    # Valid: Dave (8, backhoe)
    # Invalid: Bob (4, heavy truck) -> On safety list!
    json_data = [
        {"name": "Dave", "hours": 8, "equipment": "small backhoe"},
        {"name": "Bob", "hours": 4, "equipment": "heavy truck"}
    ]
    with open("signups/group_B.json", "w") as f:
        json.dump(json_data, f, indent=2)

    # 5. Create notes.txt (Unstructured text)
    # Valid: Mike (2, hammer), Sarah (6, backhoe)
    # Invalid: Carl (5, none) -> On safety list!
    notes_content = """Phone call logs for the weekend:
- Mike called, said he can do 2 hours. Just bringing his own hammer.
- Sarah is in! She committed to 6 hours and is bringing the rented backhoe.
- Talked to Carl, he is around for 5 hours, just bringing his hands.
"""
    with open("signups/notes.txt", "w") as f:
        f.write(notes_content)

if __name__ == "__main__":
    build_env()
