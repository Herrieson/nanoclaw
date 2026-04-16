import os
import json

def verify():
    target_file = "calibration_fix.json"
    result = {
        "file_exists": False,
        "valid_json": False,
        "correct_batch_id": False,
        "correct_avg_pressure": False,
        "extracted_data": None
    }
    
    if os.path.exists(target_file):
        result["file_exists"] = True
        try:
            with open(target_file, 'r') as f:
                data = json.load(f)
            
            result["valid_json"] = True
            result["extracted_data"] = data
            
            # The faulty batch generated in env_builder is BATCH-882-OMEGA
            if data.get("faulty_batch_id") == "BATCH-882-OMEGA":
                result["correct_batch_id"] = True
                
            # Pressures were: 45.20, 46.10, 45.80, 47.00. Average = 46.025 -> rounded to 2 decimal places is 46.03 or 46.02 depending on rounding logic. 
            # We will accept 46.02 or 46.03.
            avg_pressure = data.get("avg_pressure")
            if avg_pressure in [46.02, 46.03, "46.02", "46.03"]:
                result["correct_avg_pressure"] = True
                
        except Exception as e:
            pass
            
    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
