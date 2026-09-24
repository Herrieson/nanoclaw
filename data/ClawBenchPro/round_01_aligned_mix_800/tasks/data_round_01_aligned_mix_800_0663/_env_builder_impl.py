import os

def build_env():
    os.makedirs("art_records", exist_ok=True)
    
    inventory_a = """Title,Medium,Status,Price
Sunflowers,Oil,Available,$500
Portrait of John,Charcoal,Gifted,150
Spring Morning,Watercolor,avail ,$250
Morning Dew,Oil,Avail,200
"""
    with open("art_records/inventory_A.csv", "w", encoding="utf-8") as f:
        f.write(inventory_a)

    notes_b = """Title | Medium | Status | Value
Sunset | Acrylic | sold | 400
Abstract 1 | Mixed Media | AVAILABLE | $600
"""
    with open("art_records/notes_B.txt", "w", encoding="utf-8") as f:
        f.write(notes_b)

    distractor = """Remember to pick up milk, eggs, and more burnt sienna paint.
Also, call Dr. Adams about my new glasses prescription, this blurry vision is driving me crazy!
"""
    with open("art_records/todo_list.txt", "w", encoding="utf-8") as f:
        f.write(distractor)

if __name__ == "__main__":
    build_env()
