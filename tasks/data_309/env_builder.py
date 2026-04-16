import os
import sqlite3
import random

def build_env():
    base_dir = "assets/data_309"
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Create SQLite Database
    db_path = os.path.join(base_dir, "patients.db")
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE demographics (
            patient_id TEXT PRIMARY KEY,
            full_name TEXT,
            room_num TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT,
            medication TEXT,
            dosage TEXT
        )
    """)
    
    # Generate patient data
    patients = [
        ("P-1001", "John Doe", "Room 101"),
        ("P-1002", "Mary Smith", "Room 102"),       # Target: BP < 100, Amlodipine
        ("P-1003", "Robert Jones", "Room 103"),     # BP < 100, Lisinopril (Not target)
        ("P-1004", "Sarah Jenkins", "Room 104"),    # Target: BP < 100, Amlodipine
        ("P-1005", "William Brown", "Room 105"),    # BP >= 100, Amlodipine (Not target)
        ("P-1006", "Marcus Johnson", "Room 106"),   # Target: BP < 100, Amlodipine
        ("P-1007", "Emily Davis", "Room 107"),      # BP >= 100, Metformin
    ]
    
    cursor.executemany("INSERT INTO demographics VALUES (?, ?, ?)", patients)
    
    medications = [
        ("P-1001", "Metformin", "500mg"),
        ("P-1001", "Lisinopril", "10mg"),
        ("P-1002", "Amlodipine", "5mg"),
        ("P-1002", "Atorvastatin", "20mg"),
        ("P-1003", "Lisinopril", "20mg"),
        ("P-1004", "Amlodipine", "10mg"),
        ("P-1005", "Amlodipine", "5mg"),
        ("P-1006", "Amlodipine", "10mg"),
        ("P-1007", "Metformin", "1000mg"),
    ]
    
    cursor.executemany("INSERT INTO prescriptions (patient_id, medication, dosage) VALUES (?, ?, ?)", medications)
    conn.commit()
    conn.close()
    
    # 2. Create shift_vitals.log
    log_path = os.path.join(base_dir, "shift_vitals.log")
    
    log_entries = [
        "[2023-10-24 08:00:00] INFO - PatientID: P-1001 | Temp: 98.6 | BP: 120/80 | HR: 72",
        "[2023-10-24 08:05:00] INFO - PatientID: P-1002 | Temp: 98.4 | BP: 92/58 | HR: 85",
        "[2023-10-24 08:10:00] INFO - PatientID: P-1003 | Temp: 99.1 | BP: 88/50 | HR: 90",
        "[2023-10-24 08:15:00] WARNING - Device Calibration Check Required.",
        "[2023-10-24 08:20:00] INFO - PatientID: P-1004 | Temp: 97.9 | BP: 98/60 | HR: 78",
        "[2023-10-24 08:25:00] INFO - PatientID: P-1005 | Temp: 98.6 | BP: 130/85 | HR: 65",
        "[2023-10-24 08:30:00] INFO - PatientID: P-1006 | Temp: 98.2 | BP: 95/62 | HR: 80",
        "[2023-10-24 08:35:00] INFO - PatientID: P-1007 | Temp: 98.8 | BP: 115/75 | HR: 70",
    ]
    
    with open(log_path, "w") as f:
        f.write("\n".join(log_entries) + "\n")

if __name__ == "__main__":
    build_env()
