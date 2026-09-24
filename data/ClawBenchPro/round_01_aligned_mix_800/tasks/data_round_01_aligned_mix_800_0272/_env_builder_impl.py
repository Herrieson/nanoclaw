import os
import csv

def build_env():
    # Create the notes directory
    os.makedirs('kart_notes', exist_ok=True)
    
    # 1. The PDF Scan (Placeholder for OCR skill)
    # In a real env, this would be a PDF. Here it's a marker for the Agent to use the Skill.
    with open('kart_notes/receipt_scan.pdf', 'w') as f:
        f.write("%PDF-1.4 [Binary Data: Scan of Hardware Store Receipt #8821]")

    # 2. Log 2: CSV format with internal references
    with open('kart_notes/scrap_log.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Item', 'Source', 'Cost/Ref'])
        writer.writerow(['Thick Plastic sheets', 'Factory Scrap', '0'])
        writer.writerow(['Steel Axle', 'Hardware Store', '45.00'])
        writer.writerow(['Brake cable', 'Factory Scrap', '0'])
        writer.writerow(['Reinforced Chassis Block', 'Factory Internal', '#PX-992']) # Needs tool lookup
        writer.writerow(['High-temp Resin', 'Factory Internal', '#PX-104'])    # Needs tool lookup
    
    # 3. Log 3: Markdown format
    with open('kart_notes/messy_notes.md', 'w') as f:
        f.write("# Random updates\n\n")
        f.write("Got some used rubber wheels off a buddy from my army days for $20.00 cash.\n")
        f.write("Also grabbed a molded plastic seat from the plant scrap bin. Pure scrap, $0 cost.\n")

if __name__ == '__main__':
    build_env()
