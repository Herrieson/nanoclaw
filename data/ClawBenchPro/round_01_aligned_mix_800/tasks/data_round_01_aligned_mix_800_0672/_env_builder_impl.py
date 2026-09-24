import os
import csv

def build_env():
    os.makedirs('kart_notes', exist_ok=True)
    
    # Receipt 1: Text format
    with open('kart_notes/receipt_1.txt', 'w') as f:
        f.write("Weekend hardware store run:\n")
        f.write("- steering wheel: $35.50\n")
        f.write("- bolts and washers: $4.20\n")
        f.write("- heavy duty glue: $0.00 (returned it)\n")
    
    # Log 2: CSV format
    with open('kart_notes/scrap_log.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Item', 'Source', 'Cost'])
        writer.writerow(['Thick Plastic sheets', 'Factory Scrap', '0'])
        writer.writerow(['Steel Axle', 'Hardware Store', '45.00'])
        writer.writerow(['Brake cable', 'Factory Scrap', '0'])
        writer.writerow(['Headlights', 'Hardware Store', '0']) # Got them for free with a coupon
    
    # Log 3: Markdown format
    with open('kart_notes/messy_notes.md', 'w') as f:
        f.write("# Random updates\n\n")
        f.write("Got some used rubber wheels off a buddy from my army days for $20.00 cash.\n")
        f.write("Also grabbed a molded plastic seat from the plant scrap bin. Perfect fit.\n")

if __name__ == '__main__':
    build_env()
