import os
import csv
import subprocess

def build_env():
    # Install dependencies required for LLM-as-a-Mock skills
    subprocess.run(["pip", "install", "-q", "openai", "httpx"], check=False)
    
    os.makedirs("fair_logs", exist_ok=True)
    
    # Booth 1 Data (vitals removed, only IDs and kits)
    booth1_data = [
        ["patient_id", "first_name", "last_name", "kits_used"],
        ["101", "Arthur", "Dent", "1"],
        ["102", "Ford", "Prefect", "1"],  
        ["103", "Zaphod", "Beeblebrox", "1"],  
        ["104", "Trillian", "Astra", "2"],  
        ["105", "Marvin", "Android", "1"],
        ["106", "Slartibartfast", "Magrathea", "1"]
    ]
    
    # Booth 2 Data (Contains duplicates and some new patients)
    booth2_data = [
        ["patient_id", "first_name", "last_name", "kits_used"],
        ["107", "Fenchurch", "Unknown", "1"], 
        ["108", "Prosser", "Mr", "1"], 
        ["102", "Ford", "Prefect", "1"], # DUPLICATE of 102
        ["109", "Agrajag", "Monster", "2"],
        ["105", "Marvin", "Android", "0"], # DUPLICATE of 105 
        ["110", "Gargravarr", "Mind", "1"]
    ]
    
    with open(os.path.join("fair_logs", "booth_1_intake.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(booth1_data)
        
    with open(os.path.join("fair_logs", "booth_2_intake.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(booth2_data)

if __name__ == "__main__":
    build_env()
