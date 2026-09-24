import os

def build_env():
    # Execute in the current working directory, which is already set to the sandbox root.
    os.makedirs("messy_notes", exist_ok=True)
    
    # Week 1 donations - raw text
    with open("messy_notes/donations_week1.txt", "w", encoding="utf-8") as f:
        f.write("Donations collected by Carlos from the crew (Week 1):\n")
        f.write("--------------------------------------------------\n")
        f.write("- Juan gave $500\n")
        f.write("- Pedro gave $200 (bounced! bank rejected it, do not count)\n")
        f.write("- Carlos chipped in $300\n")
        f.write("- Mateo: $150 (cancelled his pledge)\n")

    # Week 2 donations - dirty csv
    with open("messy_notes/donations_week2.csv", "w", encoding="utf-8") as f:
        f.write("Name,Amount,Status\n")
        f.write("Miguel,1000,cleared\n")
        f.write("Luis,50,cancelled\n")
        f.write("Hector,2000,cleared\n")
        f.write("Jorge,100,bounced\n")

    # Expenses log - mixed notes
    with open("messy_notes/gastos.log", "w", encoding="utf-8") as f:
        f.write("Expenses for the event / Gastos del evento:\n")
        f.write("===========================================\n")
        f.write("1. Mariachi Los Tigres: $800.00\n")
        f.write("2. Tamales y Carnitas para la gente: $350\n\n")
        f.write("Note from Pastor: We needed a city permit for the street which was $50, but the CHURCH PAID THIS ALREADY directly from their own account. Do NOT subtract this $50 from our raised funds!!\n")

if __name__ == "__main__":
    build_env()
