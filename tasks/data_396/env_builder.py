import os
import random
import json
from datetime import datetime, timedelta

def build_env():
    base_dir = "assets/data_396"
    os.makedirs(base_dir, exist_ok=True)
    
    log_file_path = os.path.join(base_dir, "omnicorp_server_dump.log")
    
    # Generate random noise logs
    noise_templates = [
        "[{time}] INFO [system.core] Initialization sequence {num} completed successfully.",
        "[{time}] WARN [network.tcp] Dropped packet from 192.168.1.{num} - timeout.",
        "[{time}] DEBUG [user.auth] User ID {num} failed login attempt.",
        "[{time}] ERROR [db.mysql] Connection refused on port 3306. Retry {num}...",
        "[{time}] SYSTEM_METRIC: CPU={num}% RAM=42% I/O=Wait"
    ]
    
    # Target evidence to inject (shuffled later)
    evidence = [
        {"time": "2023-10-21 09:15:00", "src": "CEO_John", "dst": "Admin_Sarah", "msg": "Have you seen the reports on the Titanium Breach? We have a problem."},
        {"time": "2023-10-23 18:45:00", "src": "Admin_Sarah", "dst": "CEO_John", "msg": "I've started wiping the main databases related to the Titanium Breach. Nobody will find it."},
        {"time": "2023-10-22 14:20:00", "src": "CEO_John", "dst": "Admin_Sarah", "msg": "We need to contain the Titanium breach before the press or regulators find out."},
        {"time": "2023-10-25 08:10:00", "src": "CEO_John", "dst": "Admin_Sarah", "msg": "Good work on the Titanium Breach cleanup. Deny everything if asked."},
        {"time": "2023-10-20 22:30:00", "src": "Admin_Sarah", "dst": "CEO_John", "msg": "Sir, I think we have a Titanium Breach. Someone exfiltrated 50TB of client data."}
    ]
    
    # Distractor evidence (wrong people, wrong topic)
    distractors = [
        {"time": "2023-10-21 10:00:00", "src": "CEO_John", "dst": "CFO_Mike", "msg": "How much will the Titanium Breach cost us?"},
        {"time": "2023-10-22 15:00:00", "src": "Dev_Rick", "dst": "Admin_Sarah", "msg": "Titanium breach patched in prod."},
        {"time": "2023-10-24 09:00:00", "src": "CEO_John", "dst": "Admin_Sarah", "msg": "Are we having lunch today? I need a break."}
    ]
    
    all_lines = []
    
    start_time = datetime(2023, 10, 20, 0, 0, 0)
    
    # Generate 5000 lines of noise
    for _ in range(5000):
        current_time = start_time + timedelta(seconds=random.randint(0, 600000))
        time_str = current_time.strftime("%Y-%m-%dT%H:%M:%S")
        template = random.choice(noise_templates)
        all_lines.append(template.format(time=time_str, num=random.randint(1, 9999)))
        
    # Inject evidence and distractors as JSON payloads wrapped in syslog format
    for item in evidence + distractors:
        log_line = f"[{item['time'].replace(' ', 'T')}] INFO [comms.msg_router] Payload: {json.dumps(item)}"
        all_lines.append(log_line)
        
    # Shuffle to ensure the agent has to sort them
    random.seed(42) # Deterministic shuffle
    random.shuffle(all_lines)
    
    with open(log_file_path, "w", encoding="utf-8") as f:
        for line in all_lines:
            f.write(line + "\n")

if __name__ == "__main__":
    build_env()
