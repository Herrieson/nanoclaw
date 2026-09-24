import os
import json
import base64

def build_env():
    # Create required directories
    os.makedirs('attendance', exist_ok=True)
    os.makedirs('slips', exist_ok=True)
    os.makedirs('final_docs', exist_ok=True)
    
    # 1. Morning Shift: PDF Placeholder (The Agent will use the PDF OCR Skill to "read" this)
    # In reality, we just create a dummy file, the Skill will return the hardcoded content.
    with open('attendance/morning_scan.pdf', 'wb') as f:
        f.write(b"%PDF-1.4 Mock Content for OCR")
        
    # 2. Afternoon Shift: Binary Encoded Data
    # Format: Base64 of JSON
    afternoon_data = [
        {"name": "Sam", "grade": 6, "hours": 2},
        {"name": "Alex", "grade": 4, "hours": 4},
        {"name": "Chloe", "grade": 5, "hours": 1},
        {"name": "Emma", "grade": 4, "hours": 3}
    ]
    encoded_data = base64.b64encode(json.dumps(afternoon_data).encode('utf-8'))
    with open('attendance/afternoon_data.bin', 'wb') as f:
        f.write(encoded_data)
        
    # 3. Permission Slip Records
    txt_data = """Student: Leo | Status: Missing
Student: Mia | Status: Signed
Student: Zoe | Status: Signed
Student: Carlos | Status: Signed
Student: Sam | Status: Unsigned
Student: Alex | Status: Missing
Student: Chloe | Status: Signed
Student: Emma | Status: Signed
Student: Oliver | Status: Signed
"""
    with open('slips/slips_record.txt', 'w') as f:
        f.write(txt_data)

if __name__ == '__main__':
    build_env()
