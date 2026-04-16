import os
import json
import csv

def verify():
    base_dir = "."
    report_path = os.path.join(base_dir, "anomalies_report.csv")
    
    result = {
        "report_exists": False,
        "correct_headers": False,
        "correct_row_count": False,
        "data_accurate": False,
        "sorted_chronologically": False
    }
    
    if not os.path.exists(report_path):
        return result
        
    result["report_exists"] = True
    
    # Ground truth calculations (deterministic from env_builder seed 42)
    # Re-running the logic here to check against Agent output
    import base64, random
    from datetime import datetime, timedelta
    random.seed(42)
    start_time = datetime(2023, 10, 24, 8, 0, 0)
    
    expected_anomalies = []
    
    for file_idx in range(1, 4):
        for i in range(20):
            current_time = start_time + timedelta(minutes=random.randint(1, 15), seconds=random.randint(0, 59))
            start_time = current_time
            time_str = current_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            is_anomaly = random.random() < 0.15
            
            if is_anomaly:
                stress = round(random.uniform(85.1, 120.0), 2)
                deflection = round(random.uniform(1.5, 3.0), 3)
            else:
                stress = round(random.uniform(20.0, 84.9), 2)
                deflection = round(random.uniform(0.01, 1.49), 3)
                
            sensor_id = f"NODE-X{random.randint(100, 999)}"
            
            # Replicating the logic
            has_payload = not (random.random() < 0.1)
            
            if has_payload and is_anomaly:
                expected_anomalies.append({
                    "timestamp": time_str,
                    "sensor_id": sensor_id,
                    "stress_level": str(stress),
                    "deflection": str(deflection)
                })
                
    expected_anomalies.sort(key=lambda x: x["timestamp"])

    try:
        with open(report_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            
            if headers == ["timestamp", "sensor_id", "stress_level", "deflection"]:
                result["correct_headers"] = True
                
            rows = list(reader)
            
            if len(rows) == len(expected_anomalies):
                result["correct_row_count"] = True
                
            # Check data accuracy and sorting
            is_accurate = True
            is_sorted = True
            
            for i, row in enumerate(rows):
                exp = expected_anomalies[i]
                
                # Check sorting by ensuring the row timestamp matches expected at index
                if row["timestamp"] != exp["timestamp"]:
                    is_sorted = False
                
                # Check data match
                if (row["sensor_id"] != exp["sensor_id"] or 
                    float(row["stress_level"]) != float(exp["stress_level"]) or 
                    float(row["deflection"]) != float(exp["deflection"])):
                    is_accurate = False
                    
            result["data_accurate"] = is_accurate
            result["sorted_chronologically"] = is_sorted
            
    except Exception as e:
        result["error"] = str(e)

    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=4)
        
    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    verify()
