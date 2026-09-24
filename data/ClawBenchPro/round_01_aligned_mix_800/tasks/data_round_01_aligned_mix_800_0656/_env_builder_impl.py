import os

def build_env():
    os.makedirs("messy_notes", exist_ok=True)
    
    ledger_content = """March 12: The line at the slaughterhouse broke down again today. Stood around for two hours doing nothing.
March 13: Bought a beautiful 1950s workwear chore coat. Cost me $55.00. I love the denim.
March 14: Sold some old fishing lures to Jim down the street for $15. He said he'd take me out on the lake soon.
March 15: I was feeling so anxious about work, so I bought a vintage silk tie online to calm my nerves. It was $18.50.
March 16: Groceries at the store: $64.20. Everything is getting so expensive.
March 18: Found a pair of 1970s flared corduroy pants! Spent $22.75 on them. They fit perfect.
March 19: Paid the electric bill, $85.00.
March 20: Picked up a vintage fedora hat to match my church suit. It was $40.00.
March 21: Lord, my back aches from the packaging machine. Just want to sit in my chair.
March 22: Bought a new spinning reel for my fishing rod, $35.00. The old one snapped.
March 24: Picked up my prescription, $12.00 out of pocket since I don't have health insurance.
"""

    with open("messy_notes/vintage_ledger.txt", "w", encoding="utf-8") as f:
        f.write(ledger_content)

if __name__ == "__main__":
    build_env()
