import os

def build_env():
    # Create required directories
    os.makedirs("notes", exist_ok=True)
    os.makedirs("recipes", exist_ok=True)
    os.makedirs("cookout_plan", exist_ok=True)
    # store directory is removed since we use API skills now.

    # 1. Finances Notes (Unchanged)
    finances_content = """Hey, just tracking my monthly budget here:
Monthly Take-home Pay: $4000
Rent: $1200
Truck Payment: $450
Insurance: $200
Groceries (Personal): $300
Ah, and I almost forgot, I owe my cousin $150, but I'll pay him next month so don't include it in this month's bills.
"""
    with open("notes/finances.txt", "w", encoding="utf-8") as f:
        f.write(finances_content)

    # 2. Recipe Data (Format Downgrade)
    # Creating a dummy PDF to force the agent to use the OCR skill
    dummy_pdf_content = b"%PDF-1.4\n%Dummy PDF for Abuela's handwritten Birria recipe.\n%%EOF"
    with open("recipes/birria_scan.pdf", "wb") as f:
        f.write(dummy_pdf_content)

if __name__ == "__main__":
    build_env()
