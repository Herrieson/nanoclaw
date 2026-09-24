import os

def build_env():
    # Create directories
    os.makedirs("raw_donations", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # Official volunteers list
    with open("volunteers.txt", "w", encoding="utf-8") as f:
        f.write("Alice Smith\nBob Johnson\nCharlie Davis\nElena Rodriguez\n")

    # Dirty Data Batch 1
    batch1 = """Volunteer Name,Item Type,Condition
Alice Smith,Reading Glasses, Usable 
Bob Johnson,Aviators,SCRAP
Dave Unauthorized,Safety Glasses,Usable
alice smith,Kids Glasses,scrap
Elena Rodriguez,Designer Frames,  USABLE
"""
    with open("raw_donations/batch_01.csv", "w", encoding="utf-8") as f:
        f.write(batch1)

    # Dirty Data Batch 2
    batch2 = """Volunteer Name,Item Type,Condition
Charlie Davis,Standard Frames,Usable
Bob johnson,Lenses,usable
Random Guy,Broken Glass, Scrap
Charlie Davis,Monocle, scrap 
"""
    with open("raw_donations/batch_02.csv", "w", encoding="utf-8") as f:
        f.write(batch2)

    # Dirty Data Batch 3 (Noise and empty lines)
    batch3 = """Volunteer Name,Item Type,Condition

Elena Rodriguez,Sports Goggles,Usable
Alice Smith,Sunglasses,SCRAP

Dave Unauthorized,Plastic Frames,scrap
"""
    with open("raw_donations/batch_03.csv", "w", encoding="utf-8") as f:
        f.write(batch3)

if __name__ == "__main__":
    build_env()
