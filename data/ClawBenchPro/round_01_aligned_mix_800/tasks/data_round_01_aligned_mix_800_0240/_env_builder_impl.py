import os

def build():
    os.makedirs("messy_desk", exist_ok=True)
    os.makedirs("clean_desk", exist_ok=True)

    # Junk files to be deleted
    with open("messy_desk/lunch_orders.txt", "w", encoding="utf-8") as f:
        f.write("Agent Smith: 2x Tacos\nAgent Johnson: 1x Burrito\n")
    
    with open("messy_desk/trash_receipts.log", "w", encoding="utf-8") as f:
        f.write("TXN_9912: $4.50 Coffee\n")

    # Important file 1: The PDF (Mocked as a text file for the skill to read)
    # In a real scenario, this would be a PDF, here the Skill will handle the 'reading'
    with open("messy_desk/maintenance_logs.pdf", "w", encoding="utf-8") as f:
        f.write("[OCR SCAN DATA]\n")
        f.write("Log 1: Unit 10A - Replace lightbulb.\n")
        f.write("Log 2: Unit 12B - URGENT: Front door lock is completely broken, tenant feels unsafe.\n")
        f.write("Log 3: Lobby - Massive LEAK coming from the ceiling AC vent.\n")

    # Important file 2: Open House Notes
    with open("messy_desk/open_house_notes.txt", "w", encoding="utf-8") as f:
        f.write("Note A: Guest 1 loved the kitchen.\n")
        f.write("Note B: Guest 2 reported a URGENT plumbing issue, water everywhere in bathroom!\n")
        f.write("Note C: Guest 4 noticed a small LEAK under the kitchen sink.\n")

if __name__ == "__main__":
    build()
