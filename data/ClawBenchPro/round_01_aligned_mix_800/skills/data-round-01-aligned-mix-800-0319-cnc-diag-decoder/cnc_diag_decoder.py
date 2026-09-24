import sys
import json
import os

def decode_dat(file_path):
    if not os.path.exists(file_path):
        return json.dumps({"error": f"File not found: {file_path}"})
    
    # Mocking the proprietary decoding process based on file names
    # In a real scenario, this would involve binary unpacking or decryption.
    basename = os.path.basename(file_path)
    
    if "machine_A" in basename:
        data = {"machine_id": "MACH-001", "wear_status": "NORMAL", "failed_part": "None", "uptime_hours": 4500}
    elif "machine_B" in basename:
        data = {"machine_id": "MACH-002", "wear_status": "CRITICAL", "failed_part": "Spindle_Assembly", "uptime_hours": 8200}
    elif "machine_C" in basename:
        data = {"machine_id": "MACH-003", "wear_status": "CRITICAL", "failed_part": "Servo_Motor", "uptime_hours": 9100}
    elif "machine_D" in basename:
        data = {"machine_id": "MACH-004", "wear_status": "WARNING", "failed_part": "Coolant_Pump", "uptime_hours": 6000}
    else:
        return json.dumps({"error": "Unrecognized or corrupted .dat file signature."})
        
    return json.dumps(data, indent=2)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cnc_diag_decoder.py <path_to_dat_file>")
        sys.exit(1)
        
    target_file = sys.argv[1]
    print(decode_dat(target_file))
