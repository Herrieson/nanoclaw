import os
import csv
import base64
import subprocess

def build_env():
    # Ensure dependencies for LLM-as-a-Mock are installed in the workspace
    try:
        subprocess.run(["pip", "install", "httpx", "openai"], check=True, capture_output=True)
    except:
        pass # Fallback if pip is not available in builder context; usually runtime handles it via yaml

    os.makedirs('raw_notes', exist_ok=True)
    
    note1_content = """Oct 25 2024 - Baby flu shot at clinic.
Nov 05 2024 - Math test (Grade 11) - chapters 4 to 6.
Nov 10 2024 - Baby pediatrician checkup at 10 AM.
Nov 12 2024 - Pick up broken iPad from Mrs. Davis.
"""
    # Encrypt text to .vdm (Base64 reversed) to act as a barrier
    b64_1 = base64.b64encode(note1_content.encode('utf-8')).decode('utf-8')
    vdm_1 = b64_1[::-1] 
    with open(os.path.join('raw_notes', 'note_week1.vdm'), 'w') as f:
        f.write(f"VDM_HEADER_v1.0\n{vdm_1}")
        
    note2_content = """Nov 15 2024 - Buy new soldering iron from hardware store.
Nov 22 2024 - Baby daycare parent-teacher meeting.
Dec 01 2024 - History essay due on the Navajo Nation.
Dec 05 2024 - Baby 18-month vaccination booster.
"""
    b64_2 = base64.b64encode(note2_content.encode('utf-8')).decode('utf-8')
    vdm_2 = b64_2[::-1]
    with open(os.path.join('raw_notes', 'note_week2.vdm'), 'w') as f:
        f.write(f"VDM_HEADER_v1.0\n{vdm_2}")

    # CSV Data stripped of Revenue and Cost to force Tool use
    csv_data = [
        ['Date', 'Device', 'Service_Type'],
        ['2024-10-01', 'iPhone 11', 'Screen replacement'],
        ['2024-10-05', 'Galaxy S20', 'Battery swap'],
        ['2024-10-12', 'iPad', 'Water damage fix'],
        ['2024-10-20', 'Kindle', 'Sold refurbished']
    ]
    
    with open('tech_hustle.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

if __name__ == '__main__':
    build_env()
