import os

def build_env():
    base_dir = "assets/data_329/notes"
    os.makedirs(base_dir, exist_ok=True)
    
    monday = """Started the day late. Humming Cielito Lindo as usual.
Maria V. | Haircut | $40 | Paid
Juana | Full Color | $90 | Did not pay
Expense | Walmart - School supplies | $45.50
Elena | Styling | $50 | Paid
"""
    tuesday = """Busy day.
Carmen, Trim, $25, Paid
Expense, Target - Kids clothes, $60.00
Lucia, Highlights, $110, Not paid yet
"""
    wednesday = """Tired today.
Sofia - Balayage - $150 - PAID
Betty - Kids cut - $20 - Paid
Expense - Pharmacy - $15.00
"""
    thursday = """Rosa : Haircut : $45 : Paid
Lupe : Blowout : $35 : Paid
Expense : School trip fee : $20.00
"""
    
    with open(os.path.join(base_dir, "monday.txt"), "w") as f:
        f.write(monday)
    with open(os.path.join(base_dir, "tuesday.csv"), "w") as f:
        f.write(tuesday)
    with open(os.path.join(base_dir, "wednesday.log"), "w") as f:
        f.write(wednesday)
    with open(os.path.join(base_dir, "thursday.notes"), "w") as f:
        f.write(thursday)

if __name__ == "__main__":
    build_env()
