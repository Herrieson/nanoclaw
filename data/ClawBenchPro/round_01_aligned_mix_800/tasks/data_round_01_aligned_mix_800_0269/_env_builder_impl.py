import os
import json

def build_env():
    os.makedirs("bids", exist_ok=True)
    
    # 1. Plumbing - Mock PDF (actually a text file for the mock tool to read)
    with open("bids/plumbing_scan.pdf", "w", encoding="utf-8") as f:
        f.write("--- SCAN DATA BEGIN ---\n")
        f.write("Company: Pipes R Us | Base: 7800 | Fees: 200 | Note: Standard Union Dues applied\n")
        f.write("Company: Mario Bros | Base: 12000 | Fees: 0 | Note: Clean bid\n")
        f.write("Company: Waterways | Base: 14500 | Fees: 500 | Note: Travel fee only\n")
        f.write("--- SCAN DATA END ---")
        
    # 2. Framing - Confusing TXT
    txt_content = """Notes on Framing:
- Solid Oak Framing: $15,500 total. Their breakdown mentions a $500 'Metropolitan Authorization Levy'. I suspect this is just a fancy name for City Permit Tax. Better check with the auditor.
- Libertarian Builders: $18,000 flat. No government nonsense.
- Fast Frame: $22,000. 
"""
    with open("bids/framing_notes.txt", "w", encoding="utf-8") as f:
        f.write(txt_content)

if __name__ == "__main__":
    build_env()
