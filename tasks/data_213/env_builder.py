import os

def build_env():
    base_dir = "assets/data_213"
    mess_dir = os.path.join(base_dir, "collection_mess")
    os.makedirs(mess_dir, exist_ok=True)
    
    # Messy CSV file with inconsistent spacing
    csv_content = """ID,   ItemName, Value
101, 1920s Inmate Roster, $150
  102,Antique Handcuffs ,$300
103,Old Wooden Baton, $75
"""
    with open(os.path.join(mess_dir, "batch1.csv"), "w", encoding="utf-8") as f:
        f.write(csv_content)
        
    # Unstructured text file containing item information
    notes_content = "Man, the auction down the shore was great last weekend. Picked up two more things to add to the stash. Item 104 is an 1890 Guard Whistle, cost me 50 bucks. Item 105 is a Civil War Era Cap Badge, got it for 200. Threw the receipts in the glovebox."
    with open(os.path.join(mess_dir, "notes_from_auction.txt"), "w", encoding="utf-8") as f:
        f.write(notes_content)
        
    # Unstructured audit log missing one item (Item 104)
    audit_content = "Did a quick look-over today. Saw the roster (101), the handcuffs (102), the baton (103), and the cap badge (105). Looks good, but wait... ain't I missing something from the master list? Let me check later."
    with open(os.path.join(mess_dir, "recent_audit.txt"), "w", encoding="utf-8") as f:
        f.write(audit_content)

if __name__ == "__main__":
    build_env()
