import os
import json

def build_env():
    os.makedirs("bids", exist_ok=True)
    
    # Plumbing CSV
    with open("bids/plumbing.csv", "w", encoding="utf-8") as f:
        f.write("Company,BaseCost,Fees,Notes\n")
        f.write("Pipes R Us,7800,200,Union Dues\n")
        f.write("Mario Bros,12000,0,None\n")
        f.write("Waterways,14500,500,Travel fee\n")
        
    # Electrical JSON
    elec = [
        {"company": "Sparky's", "cost": 9000, "line_items": [{"name": "materials", "price": 4000}, {"name": "labor", "price": 5000}]},
        {"company": "Volt City", "cost": 8600, "line_items": [{"name": "materials", "price": 3000}, {"name": "labor", "price": 5500}, {"name": "Union Dues", "price": 100}]}
    ]
    with open("bids/electrical.json", "w", encoding="utf-8") as f:
        json.dump(elec, f, indent=2)
        
    # Framing TXT
    txt_content = """Quote from Solid Oak Framing: Total cost is $15,500. This includes $15,000 for labor and materials, and a $500 City Permit Tax.
Quote from Libertarian Builders: I'll do it for $18,000 flat. No government fees.
Quote from Fast Frame: $22,000. Easy job.
"""
    with open("bids/framing.txt", "w", encoding="utf-8") as f:
        f.write(txt_content)

if __name__ == "__main__":
    build_env()
