import os
import json

def build_env():
    os.makedirs("records", exist_ok=True)

    messy_text = """
    >>> LOST & FOUND LOG - Neon Galaxy MD <<<
    1. Found: Blue Jacket | Name: Marcus Johnson | Location: Arcade
    2. Item: dirty sock - Name: NONE, Location: Bathroom
    3. Apple Watch (Owner: Sarah Connor) found at Laser Tag
    4. keys... Owner: N/A ... Lobby
    5. Found: Gold Ring | Owner: David Smith | Location: VR Room
    6. Item: water bottle | Name:  | Location: Entrance
    7. VR Headset piece [Name: Chloe Bennett] (Loc: VR Room)
    8. Unknown item: loose change. Name: null.
    """
    
    with open("records/messy_lost_and_found.txt", "w", encoding="utf-8") as f:
        f.write(messy_text.strip())

    vips = [
        {"id": 101, "name": "Marcus Johnson", "tier": "Gold"},
        {"id": 102, "name": "Sarah Connor", "tier": "Platinum"},
        {"id": 103, "name": "Alice Wonderland", "tier": "Silver"},
        {"id": 104, "name": "Chloe Bennett", "tier": "Gold"}
    ]
    
    with open("records/vips.json", "w", encoding="utf-8") as f:
        json.dump(vips, f, indent=4)

if __name__ == "__main__":
    build_env()
