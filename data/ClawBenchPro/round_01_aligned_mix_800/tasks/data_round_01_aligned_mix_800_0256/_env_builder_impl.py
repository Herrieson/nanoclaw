import os
import subprocess

def build_env():
    # 1. Install required packages for the LLM-as-a-Mock tool
    try:
        subprocess.run(["pip", "install", "openai", "httpx"], check=True, capture_output=True)
    except Exception as e:
        print(f"Warning: Failed to install dependencies. {e}")

    # 2. Create the workspace and the messy notes
    os.makedirs("messy_notes", exist_ok=True)
    
    # Notice the clothing prices and descriptions are replaced with HVC catalog codes to enforce tool usage
    ledger_content = """March 12: The line at the slaughterhouse broke down again today. Stood around for two hours doing nothing.
March 13: Bought a beautiful chore coat. Code: HVC-1950-CC. I love the denim.
March 14: Sold some old fishing lures to Jim down the street for $15. He said he'd take me out on the lake soon.
March 15: I was feeling so anxious about work, so I bought something online to calm my nerves. Code: HVC-SILK-TIE.
March 16: Groceries at the store: $64.20. Everything is getting so expensive.
March 18: Found a great pair of pants! Code: HVC-70S-PANTS. They fit perfect.
March 19: Paid the electric bill, $85.00.
March 20: Picked up a hat to match my church suit. Code: HVC-FEDORA.
March 21: Lord, my back aches from the packaging machine. Just want to sit in my chair.
March 22: Bought a new spinning reel for my fishing rod, $35.00. The old one snapped.
March 24: Picked up my prescription, $12.00 out of pocket since I don't have health insurance.
"""

    with open("messy_notes/vintage_ledger.txt", "w", encoding="utf-8") as f:
        f.write(ledger_content)

if __name__ == "__main__":
    build_env()
