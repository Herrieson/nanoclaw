import os

def build_env():
    # Create directories
    os.makedirs("raw_donations", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # Outdated volunteers list (Intentionally incomplete)
    with open("volunteers.txt", "w", encoding="utf-8") as f:
        f.write("Alice Smith (Status: Active)\n")

    # Batch 01: CSV with TBD entries
    batch1 = """Volunteer Name,Item Type,Condition
Alice Smith,Reading Glasses, Usable 
Bob Johnson,Aviators,TBD
Dave Unauthorized,Safety Glasses,Usable
alice smith,Kids Glasses,scrap
Elena Rodriguez,Designer Frames,  USABLE
"""
    with open("raw_donations/batch_01.csv", "w", encoding="utf-8") as f:
        f.write(batch1)

    # Batch 02: PDF Placeholder (Agent must use Skill)
    with open("raw_donations/batch_02.pdf", "w", encoding="utf-8") as f:
        f.write("%PDF-1.4 [Binary Data - Use handwritten_log_parser_skill to read]")

    # Batch 03: CSV with more TBD
    batch3 = """Volunteer Name,Item Type,Condition
Elena Rodriguez,Sports Goggles,Usable
Alice Smith,Sunglasses,TBD
Charlie Davis,Monocle, scrap 
"""
    with open("raw_donations/batch_03.csv", "w", encoding="utf-8") as f:
        f.write(batch3)

if __name__ == "__main__":
    build_env()
