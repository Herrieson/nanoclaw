import os

def build_env():
    # Create the workspace
    os.makedirs("messy_notes", exist_ok=True)
    
    # Week 1: Mixed notes with Transaction IDs
    # Juan: $500 (ID: TXN-001 -> Cleared)
    # Pedro: $200 (ID: TXN-002 -> Bounced)
    # Carlos: $300 (Cash -> Cleared)
    with open("messy_notes/donations_week1.txt", "w", encoding="utf-8") as f:
        f.write("Crew Donations - Week 1\n")
        f.write("-----------------------\n")
        f.write("- Juan: $500 (Ref: TXN-001)\n")
        f.write("- Pedro: $200 (Ref: TXN-002)\n")
        f.write("- Carlos: $300 (Handed in cash personally)\n")
        f.write("- Mateo: $150 (Wait, he called and cancelled this morning)\n")

    # Week 2: Dirty CSV
    # Miguel: $1000 (ID: TXN-003 -> Cleared)
    # Hector: $2000 (ID: TXN-004 -> Cleared)
    # Jorge: $100 (ID: TXN-005 -> Bounced)
    with open("messy_notes/donations_week2.csv", "w", encoding="utf-8") as f:
        f.write("Name,Amount,Reference\n")
        f.write("Miguel,1000,TXN-003\n")
        f.write("Luis,50,Cancelled\n")
        f.write("Hector,2000,TXN-004\n")
        f.write("Jorge,100,TXN-005\n")

    # The PDF obstacle (Placeholder file)
    with open("messy_notes/mariachi_invoice.pdf", "w", encoding="utf-8") as f:
        f.write("%PDF-1.4 [Binary Content Emulated]\n")
        f.write("This is a simulated PDF for the Mariachi Los Tigres invoice for $800.00.")

    # Expenses log - natural language trap
    with open("messy_notes/gastos.log", "w", encoding="utf-8") as f:
        f.write("Other Expenses / Otros Gastos:\n")
        f.write("==============================\n")
        f.write("- Tamales y Carnitas: $350\n")
        f.write("- Street Permit: $50 (PAID BY CHURCH DIRECTLY, DO NOT DEDUCT FROM CREW FUND)\n")

if __name__ == "__main__":
    build_env()
