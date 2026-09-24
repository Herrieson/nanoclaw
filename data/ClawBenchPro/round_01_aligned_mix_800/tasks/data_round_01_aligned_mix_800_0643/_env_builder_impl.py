import os
import csv

def build_env():
    os.makedirs('raw_notes', exist_ok=True)
    
    note1_content = """Oct 25 2024 - Baby flu shot at clinic.
Nov 05 2024 - Math test (Grade 11) - chapters 4 to 6.
Nov 10 2024 - Baby pediatrician checkup at 10 AM.
Nov 12 2024 - Pick up broken iPad from Mrs. Davis.
"""
    with open(os.path.join('raw_notes', 'note_week1.txt'), 'w') as f:
        f.write(note1_content)
        
    note2_content = """Nov 15 2024 - Buy new soldering iron from hardware store.
Nov 22 2024 - Baby daycare parent-teacher meeting.
Dec 01 2024 - History essay due on the Navajo Nation.
Dec 05 2024 - Baby 18-month vaccination booster.
"""
    with open(os.path.join('raw_notes', 'note_week2.txt'), 'w') as f:
        f.write(note2_content)

    csv_data = [
        ['Date', 'Item', 'Revenue', 'Cost'],
        ['2024-10-01', 'Screen replacement iPhone 11', '100', '40'],
        ['2024-10-05', 'Battery swap Galaxy S20', '60', '20'],
        ['2024-10-12', 'Water damage fix iPad', '150', '30'],
        ['2024-10-20', 'Sold refurbished Kindle', '80', '0']
    ]
    
    with open('tech_hustle.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

if __name__ == '__main__':
    build_env()
