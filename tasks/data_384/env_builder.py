import os
import json
import random
import base64

def setup_environment():
    base_dir = "assets/data_384"
    os.makedirs(base_dir, exist_ok=True)

    # 1. 护林员的手写笔记 (Field Notes)
    field_notes = """
    Date: 2023-10-12
    Location: Oak Creek Basin, Sector 7G (Fire Lookout Tower)
    Observed: Oily residue, metallic smell. 
    Notes: Found a discarded 'Eco-Monitoring Unit' (EMU-X100) nearby. It seems to have recorded the spill event before it was smashed. 
    Sensor ID: EMU-7721
    Gate Sensor: The gate at the North Entrance (Gate-N4) logged a heavy vehicle exiting around the time of the leak.
    Flow Rate Constant: The creek flows at 0.5 meters per second. The chemical spread is consistent with a 120-minute leak, but check the sensor logs for exact 'Active Duration'.
    """
    with open(os.path.join(base_dir, "field_notes.txt"), "w") as f:
        f.write(field_notes)

    # 2. 模拟受损的传感器日志 (Binary/Corrupted Log)
    # 包含关键信息：Chemical: Benzene, Start_Time: 14:00, End_Time: 16:30 (150 mins)
    log_content = [
        {"timestamp": "2023-10-12T13:55:00", "sensor": "EMU-7721", "status": "OK", "reading": 0.01},
        {"timestamp": "2023-10-12T14:00:00", "sensor": "EMU-7721", "status": "ALERT", "chemical_code": "BNZ-9", "ppm": 450.5},
        {"timestamp": "2023-10-12T16:30:00", "sensor": "EMU-7721", "status": "POWER_OFF", "chemical_code": "BNZ-9", "ppm": 120.2}
    ]
    # 故意将其存储为某种编码格式或隐藏在大量冗余数据中
    with open(os.path.join(base_dir, "sensor_logs.dat"), "wb") as f:
        f.write(base64.b64encode(json.dumps(log_content).encode()))

    # 3. 门禁系统数据 (Gate Logs - CSV)
    gate_logs = [
        "timestamp,gate_id,event,payload",
        "2023-10-12T12:00:00,Gate-N4,IN,Personal Vehicle: Ranger Bob",
        "2023-10-12T13:45:00,Gate-N4,IN,Truck-ID: TRK-992-X (Owner: NovaPure Industrial)",
        "2023-10-12T16:45:00,Gate-N4,OUT,Truck-ID: TRK-992-X (Owner: NovaPure Industrial)",
        "2023-10-12T18:00:00,Gate-N4,OUT,Personal Vehicle: Ranger Bob"
    ]
    with open(os.path.join(base_dir, "gate_sensor_logs.csv"), "w") as f:
        f.write("\n".join(gate_logs))

    # 4. 物质对照表 (Chemical Mapping)
    chemical_mapping = {
        "BNZ-9": "Benzene",
        "TOL-2": "Toluene",
        "XLY-4": "Xylene"
    }
    with open(os.path.join(base_dir, "chemical_lookup.json"), "w") as f:
        json.dump(chemical_mapping, f)

if __name__ == "__main__":
    setup_environment()
