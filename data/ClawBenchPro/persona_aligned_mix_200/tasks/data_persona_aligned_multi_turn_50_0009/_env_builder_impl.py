import os
import argparse
import struct
import random
import math
import json
import csv

def generate_quaternion(valid=True):
    if not valid:
        if random.random() > 0.5:
            return 0.0, 0.0, 0.0, 0.0
        else:
            return random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(-2, 2)
    # Valid normalized quaternion
    q1, q2, q3, q4 = random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)
    mag = math.sqrt(q1**2 + q2**2 + q3**2 + q4**2)
    if mag == 0:
        return 1.0, 0.0, 0.0, 0.0
    return q1/mag, q2/mag, q3/mag, q4/mag

def pack_frame(timestamp, q, temp1, temp2, is_corrupted=False):
    # Header: 1A 2B 3C 4D
    header = bytes.fromhex("1A2B3C4D")
    payload = struct.pack("!Iffffff", timestamp, q[0], q[1], q[2], q[3], temp1, temp2)
    tail = bytes.fromhex("FFFF")
    frame = header + payload + tail
    
    if is_corrupted:
        # truncate or modify
        frame = frame[:-3] + bytes.fromhex("000000")
    
    return frame.hex().upper()

def write_hex_stream(filepath, frames, noise_level=0.3):
    with open(filepath, 'w') as f:
        stream = ""
        for frame in frames:
            if random.random() < noise_level:
                # Add random hex garbage
                stream += "".join(random.choices("0123456789ABCDEF", k=random.randint(4, 20)))
            stream += frame
            if random.random() < noise_level:
                stream += "".join(random.choices("0123456789ABCDEF", k=random.randint(4, 20)))
        
        # Split into lines
        line_length = 64
        for i in range(0, len(stream), line_length):
            f.write(stream[i:i+line_length] + "\n")

def build_turn_1():
    os.makedirs("docs", exist_ok=True)
    os.makedirs("downlink_raw/day_01", exist_ok=True)
    
    sys_dict = {
        "frame_sync": "1A2B3C4D",
        "frame_tail": "FFFF",
        "endian": "big",
        "payload": {
            "timestamp": {"offset": 4, "type": "uint32"},
            "st_q1": {"offset": 8, "type": "float32"},
            "st_q2": {"offset": 12, "type": "float32"},
            "st_q3": {"offset": 16, "type": "float32"},
            "st_q4": {"offset": 20, "type": "float32"},
            "tcs_temp_1": {"offset": 24, "type": "float32"},
            "tcs_temp_2": {"offset": 28, "type": "float32"}
        }
    }
    with open("docs/sys_dict.json", "w") as f:
        json.dump(sys_dict, f, indent=4)
        
    frames_A = []
    # Normal data
    for ts in range(10000, 10050, 5):
        frames_A.append(pack_frame(ts, generate_quaternion(True), random.uniform(20, 60), random.uniform(20, 60)))
    
    # Anomaly > 85.0
    frames_A.append(pack_frame(10060, generate_quaternion(True), 88.5, 60.0))
    frames_A.append(pack_frame(10065, generate_quaternion(True), 40.0, 92.1))
    
    # Corrupted frame (should be ignored)
    frames_A.append(pack_frame(10070, generate_quaternion(True), 99.0, 99.0, is_corrupted=True))
    
    write_hex_stream("downlink_raw/day_01/stream_A.hex", frames_A)

def build_turn_2():
    os.makedirs("downlink_raw/day_02", exist_ok=True)
    os.makedirs("maneuver_logs", exist_ok=True)
    
    events = [
        {"event_id": "OM_01", "timestamp_start": 20100, "timestamp_end": 20200, "event_type": "Orbital Maneuver"},
        {"event_id": "OM_02", "timestamp_start": 20500, "timestamp_end": 20600, "event_type": "Orbital Maneuver"}
    ]
    with open("maneuver_logs/events.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["event_id", "timestamp_start", "timestamp_end", "event_type"])
        writer.writeheader()
        writer.writerows(events)
        
    frames_B = []
    # Normal data
    for ts in range(20000, 20050, 5):
        frames_B.append(pack_frame(ts, generate_quaternion(True), random.uniform(20, 60), random.uniform(20, 60)))
    
    # High temp inside Maneuver OM_01 (should be ignored)
    frames_B.append(pack_frame(20150, generate_quaternion(True), 95.0, 40.0))
    
    # High temp outside Maneuver, ST valid (True positive temp, ST still alive)
    frames_B.append(pack_frame(20300, generate_quaternion(True), 89.0, 30.0))
    
    # High temp outside Maneuver, ST invalid (True positive temp, ST dead - TARGET condition)
    frames_B.append(pack_frame(20400, generate_quaternion(False), 92.0, 98.0))
    
    # High temp inside Maneuver OM_02, ST invalid (High temp ignored, so this should not be the final target)
    frames_B.append(pack_frame(20550, generate_quaternion(False), 105.0, 102.0))

    write_hex_stream("downlink_raw/day_02/stream_B.hex", frames_B)

def build_turn_3():
    os.makedirs("downlink_raw/day_03", exist_ok=True)
    
    cmds = """<?xml version="1.0" encoding="UTF-8"?>
<commands>
    <cmd id="RESET_HEATER" condition="temp_high_only" hex_code="A1 B2 C3 D4"/>
    <cmd id="REBOOT_ST_AND_COOL" condition="st_invalid_and_temp_high" hex_code="F5 E6 D7 C8"/>
    <cmd id="IGNORE_ROUTINE" condition="maneuver_ongoing" hex_code="00 00 00 00"/>
</commands>
"""
    with open("docs/recovery_cmds.xml", "w") as f:
        f.write(cmds)
        
    frames_C = []
    # Normal
    for ts in range(30000, 30050, 5):
        frames_C.append(pack_frame(ts, generate_quaternion(True), random.uniform(20, 60), random.uniform(20, 60)))
        
    # FATAL TARGET: Not in any maneuver (logs only went up to 20600), temp > 85, ST invalid
    frames_C.append(pack_frame(30120, generate_quaternion(False), 110.5, 80.0))
    
    write_hex_stream("downlink_raw/day_03/stream_C.hex", frames_C)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
    elif args.turn == 3:
        build_turn_3()
