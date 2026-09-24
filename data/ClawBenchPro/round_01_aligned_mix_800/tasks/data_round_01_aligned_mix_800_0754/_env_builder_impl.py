import os
import random

def build_env():
    os.makedirs("kiosk_logs", exist_ok=True)
    
    logs = [
        "[08:15 AM] NAME: John Doe | DEPT: HR Programs | REASON: Standard application follow-up.",
        "[13:45] NAME: Jane Smith | DEPT: DMV | REASON: Renew driver's license.",
        "[09:30 AM] NAME: Alice Jones | DEPT: HR Programs | REASON: Health insurance coverage dispute!! I need help immediately.",
        "[02:00 PM] NAME: Bob Brown | DEPT: HR Programs | REASON: Final interview for the clerk position.",
        "[10:15 AM] NAME: Charlie Davis | DEPT: Parks | REASON: Submitting a public park event permit.",
        "[11:00 AM] NAME: Eve Evans | DEPT: HR Programs | REASON: Benefits enrollment - confusing health insurance question.",
        "[04:30 PM] NAME: Gregory House | DEPT: HR Programs | REASON: General payroll inquiry.",
        "[08:00 AM] NAME: Sarah Connor | DEPT: DMV | REASON: Vehicle registration.",
        "[12:15 PM] NAME: Tom Clark | DEPT: HR Programs | REASON: Updating direct deposit forms."
    ]
    
    random.seed(42)
    random.shuffle(logs)
    
    with open("kiosk_logs/raw_dump.txt", "w", encoding="utf-8") as f:
        for log in logs:
            f.write(log + "\n")

if __name__ == "__main__":
    build_env()
