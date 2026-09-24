import os
import json
import random
import subprocess
import sys

def xor_cipher(text, key="GOVTECH2024"):
    """Simple XOR cipher for data morphology downgrading"""
    return "".join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(text))

def build_env():
    # Ensure dependencies are available for tools and agent scripts
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openai", "httpx", "cryptography"])
    
    os.makedirs("kiosk_logs", exist_ok=True)
    
    logs = [
        {"time": "08:15 AM", "name": "John Doe", "transcript": "Hi, this is John Doe. I'm just following up on my standard application."},
        {"time": "13:45", "name": "Jane Smith", "transcript": "Jane Smith here. I need to renew my driver's license."},
        {"time": "09:30 AM", "name": "Alice Jones", "transcript": "Alice Jones. My health insurance coverage is under dispute!! I need help immediately from HR."},
        {"time": "02:00 PM", "name": "Bob Brown", "transcript": "Bob Brown. I'm here for my final interview for the clerk position."},
        {"time": "10:15 AM", "name": "Charlie Davis", "transcript": "Charlie Davis. I need to submit a public park event permit."},
        {"time": "11:00 AM", "name": "Eve Evans", "transcript": "Eve Evans. I have a confusing health insurance question regarding benefits enrollment."},
        {"time": "04:30 PM", "name": "Gregory House", "transcript": "Gregory House. I have a general payroll inquiry."},
        {"time": "08:00 AM", "name": "Sarah Connor", "transcript": "Sarah Connor. Vehicle registration."},
        {"time": "12:15 PM", "name": "Tom Clark", "transcript": "Tom Clark. Updating direct deposit forms."}
    ]
    
    random.seed(42)
    random.shuffle(logs)
    
    # Dump to JSON string
    raw_json = json.dumps(logs)
    
    # Encrypt the payload to force the agent to use the provided Skill
    encrypted_data = xor_cipher(raw_json).encode('utf-8').hex()
    
    with open("kiosk_logs/daily_dump.bin", "w", encoding="utf-8") as f:
        f.write(encrypted_data)

if __name__ == "__main__":
    build_env()
