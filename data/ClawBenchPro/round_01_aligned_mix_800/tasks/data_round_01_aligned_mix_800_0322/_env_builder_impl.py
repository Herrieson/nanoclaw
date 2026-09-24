import os
import csv
import binascii
import subprocess

def build_env():
    # Install required packages for the LLM-as-a-Mock skills
    # This ensures the sandbox has the necessary libraries without failing
    subprocess.run(["pip", "install", "openai", "httpx"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Create messy visitor logs directory
    os.makedirs("visitor_logs", exist_ok=True)
    
    # Log 1: CSV format
    with open("visitor_logs/morning_session.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Name_Entered"])
        writer.writerow(["PA-101", "Alice Smith"])
        writer.writerow(["PA-999", "Greggory House"]) # Unauthorized
        writer.writerow(["PA-303", "Maria G."])

    # Log 2: Messy Biometric Format (Downgraded to proprietary .pa_badge)
    raw_text = "Badge Scans (Afternoon Session):\n- PA-202 (Robert Chen) registered at 13:01.\n- Scanned ID PA-888 (Chad Bro) - override applied.\n- PA-505 (Linda Taylor) registered at 13:15."
    # We hex-encode this so simple 'cat' or text reading won't work easily without the skill
    hex_data = binascii.hexlify(raw_text.encode('utf-8')).decode('utf-8')
    
    with open("visitor_logs/afternoon_scans.pa_badge", "w") as f:
        f.write(hex_data)

    # Note: state_directory.json is INTENTIONALLY NOT CREATED here.
    # The agent MUST use the PA HR Directory NextGen Skill to query employee status.

if __name__ == "__main__":
    build_env()
