import os
import csv
import json

def build_env():
    # Create required directories
    os.makedirs('attendance', exist_ok=True)
    os.makedirs('slips', exist_ok=True)
    os.makedirs('final_docs', exist_ok=True)
    
    # Generate Attendance Records (Messy formats)
    csv_data = [
        ['Student_Name', 'Grade', 'Hours'],
        ['Leo', '5', '4'],
        ['Mia', '6', '5'],
        ['Zoe', '5', '3'],
        ['Carlos', '4', '2']
    ]
    
    with open('attendance/morning_shift.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)
        
    json_data = [
        {"name": "Sam", "grade": 6, "hours": 2},
        {"name": "Alex", "grade": 4, "hours": 4},
        {"name": "Chloe", "grade": 5, "hours": 1},
        {"name": "Emma", "grade": 4, "hours": 3}
    ]
    
    with open('attendance/afternoon_shift.json', 'w') as f:
        json.dump(json_data, f)
        
    # Generate Permission Slip Records
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
