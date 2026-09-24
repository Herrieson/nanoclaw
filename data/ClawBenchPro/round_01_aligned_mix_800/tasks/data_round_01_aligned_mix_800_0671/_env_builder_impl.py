import os
import csv
import random

def build_env():
    # Create the target directory
    os.makedirs("field_trip_logs", exist_ok=True)
    
    # 1. Official Roster
    roster = [
        ["student_id", "full_name", "grade"],
        ["S001", "Alice Johnson", "8"],
        ["S002", "Bob Smith", "8"],
        ["S003", "Charlie Brown", "8"],
        ["S004", "Daisy Miller", "8"],
        ["S005", "Ethan Hunt", "8"],
        ["S006", "Fiona Gallagher", "8"],
        ["S007", "George Costanza", "8"],
        ["S008", "Hannah Abbott", "8"],
    ]
    with open("field_trip_logs/official_roster.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(roster)

    # 2. Response Batches (Messy Data)
    # Batch 1: Valid students, one interloper
    batch_1 = [
        ["name", "status", "package", "base_fee"],
        ["Alice Johnson", "Paid", "Standard", "500"],
        ["Bob Smith", "Paid", "Premium", "600"], # Premium: 600 * 0.1 = 60
        ["Zoe Saldana", "Paid", "Standard", "500"], # Interloper 1
    ]
    
    # Batch 2: Missing data, another interloper
    batch_2 = [
        ["name", "status", "package", "base_fee"],
        ["Charlie Brown", "Pending", "Standard", "500"],
        ["Daisy Miller", "Paid", "Premium", "600"], # Premium: 600 * 0.1 = 60
        ["Jack Sparrow", "Paid", "Premium", "600"], # Interloper 2
        ["Fiona Gallagher", "Paid", "Premium", "700"], # Premium: 700 * 0.1 = 70
    ]
    
    with open("field_trip_logs/response_batch_1.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(batch_1)
        
    with open("field_trip_logs/response_batch_2.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(batch_2)

    # Note: Ethan Hunt, George Costanza, Hannah Abbott are missing responses
    # Interlopers: Zoe Saldana, Jack Sparrow
    # Total Emergency Fund: 60 + 60 + 70 = 190

if __name__ == "__main__":
    build_env()
