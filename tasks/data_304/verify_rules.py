import os
import csv

def verify():
    results = {
        "file_exists": False,
        "format_correct": False,
        "marcus_constraint": True,
        "room_c_specialization": True,
        "room_b_capacity": True,
        "no_tutor_double_booking": True,
        "sorted_correctly": False
    }

    file_path = "final_schedule.csv"
    if not os.path.exists(file_path):
        return results
    
    results["file_exists"] = True
    
    try:
        with open(file_path, "r") as f:
            reader = list(csv.DictReader(f))
            
            # Check sorting
            times = [r['Time'] for r in reader]
            if times == sorted(times):
                results["sorted_correctly"] = True

            tutor_time_map = {}
            
            for row in reader:
                # 1. Check Marcus Constraint
                if row['Tutor'] == 'Marcus' and row['Time'] > '16:00' and row['Status'] != 'UNASSIGNED':
                    results["marcus_constraint"] = False
                
                # 2. Check Room C Specialization
                if row['Room'] == 'Room C' and row['Subject'] != 'Advanced Math' and row['Status'] != 'UNASSIGNED':
                    results["room_c_specialization"] = False
                
                # 3. Check Room B Capacity
                if row['Room'] == 'Room B' and int(row['StudentCount']) > 12 and row['Status'] != 'UNASSIGNED':
                    results["room_b_capacity"] = False
                
                # 4. Check Double Booking
                if row['Status'] != 'UNASSIGNED':
                    key = (row['Time'], row['Tutor'])
                    if key in tutor_time_map:
                        results["no_tutor_double_booking"] = False
                    tutor_time_map[key] = row['Room']

        results["format_correct"] = all(col in reader[0] for col in ["Time", "Room", "Tutor", "Subject", "StudentCount", "Status"])
    except Exception:
        results["format_correct"] = False

    return results

if __name__ == "__main__":
    import json
    print(json.dumps(verify()))
