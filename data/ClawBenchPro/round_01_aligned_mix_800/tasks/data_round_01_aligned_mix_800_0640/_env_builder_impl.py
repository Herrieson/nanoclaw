import os

def build():
    os.makedirs("messy_desk", exist_ok=True)
    os.makedirs("clean_desk", exist_ok=True)

    # Junk files to be deleted
    with open("messy_desk/lunch_orders.txt", "w", encoding="utf-8") as f:
        f.write("Agent Smith: 2x Tacos\nAgent Johnson: 1x Burrito, no onions\nManager: Salad\n")
    
    with open("messy_desk/trash_receipts.log", "w", encoding="utf-8") as f:
        f.write("TXN_9912: $4.50 Coffee\nTXN_9913: $12.00 Parking\n")

    # Important files to be parsed
    with open("messy_desk/maintenance_logs.txt", "w", encoding="utf-8") as f:
        f.write("Unit 10A: Replace lightbulb in hallway.\n")
        f.write("Unit 12B: URGENT - Front door lock is completely broken, tenant feels unsafe.\n")
        f.write("Unit 4C: Paint is chipping near the window.\n")
        f.write("Lobby: Massive LEAK coming from the ceiling AC vent.\n")
        f.write("Basement: Needs regular sweeping.\n")

    with open("messy_desk/open_house_notes.txt", "w", encoding="utf-8") as f:
        f.write("Guest 1: Loved the kitchen counter.\n")
        f.write("Guest 2: The master bathroom has a URGENT plumbing issue, water everywhere!\n")
        f.write("Guest 3: Thought the asking price was a bit high.\n")
        f.write("Guest 4: Noticed a small LEAK under the kitchen sink.\n")

if __name__ == "__main__":
    build()
