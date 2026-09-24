import os
import base64
import subprocess

def build_env():
    # Install required packages for the LLM-as-a-Mock skill
    try:
        subprocess.run(["pip", "install", "openai", "httpx"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass # Fallback in case pip is restricted, though python:3.10-slim should allow it.

    # Create necessary directories
    os.makedirs("restaurant_records", exist_ok=True)
    os.makedirs("messy_desk", exist_ok=True)
    os.makedirs("family_planning", exist_ok=True)

    # Helper to encode proprietary shift logs
    def encode_shift(text):
        return base64.b64encode(text.encode('utf-8')).decode('utf-8')

    # Messy timesheets in restaurant_records (now encoded as proprietary .shiftlog)
    week1_content = """Shift Log - Week 1
Date: 2023-10-09 (Mon)
Time: 09:00 - 15:00
Role: Cashier

Date: 2023-10-12 (Thu)
Time: 14:00 - 18:00
Role: Cashier
Notes: Very busy shift!
"""
    with open(os.path.join("restaurant_records", "w1_shifts.shiftlog"), "w") as f:
        f.write(encode_shift(week1_content))

    week2_content = """Shift Log - Week 2
Date: 2023-10-17 (Tue)
Time: 10:00 - 16:00

Date: 2023-10-20 (Fri)
Time: 08:00 - 14:00
"""
    with open(os.path.join("restaurant_records", "w2_shifts.shiftlog"), "w") as f:
        f.write(encode_shift(week2_content))

    week3_content = """Shift Log - Week 3
Hey, just one shift for you this week.
Date: 2023-10-26 (Thu)
Time: 16:00 - 20:00
Role: Cashier
"""
    with open(os.path.join("restaurant_records", "w3_shifts.shiftlog"), "w") as f:
        f.write(encode_shift(week3_content))
        
    # Add some distracting files in messy_desk
    receipt_content = """Libreria Mexico - Receipt
1x El Laberinto de la Soledad - $15.99
1x Como Agua para Chocolate - $12.50
Total: $28.49
"""
    with open(os.path.join("messy_desk", "book_receipt.txt"), "w") as f:
        f.write(receipt_content)
        
    grocery_content = """Supermercado
Milk: $3.50
Eggs: $4.20
Tortillas: $2.10
Total: $9.80
"""
    with open(os.path.join("messy_desk", "groceries.txt"), "w") as f:
        f.write(grocery_content)

if __name__ == "__main__":
    build_env()
