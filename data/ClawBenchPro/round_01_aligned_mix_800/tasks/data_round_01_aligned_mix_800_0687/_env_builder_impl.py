import os
import csv

def build_env():
    # Create directories
    os.makedirs("raw_data/faculty_logs", exist_ok=True)
    
    # Create the policy file
    policy_content = """UNIVERSITY PROCEDURAL GUIDELINE - TIME ALLOCATION
As per state funding mandates and university efficiency protocols, faculty members must prioritize Teaching and Research. 
Under no circumstances should 'Administrative' duties exceed 20% of a faculty member's total logged hours for any given period.
Violators will be subject to a workload audit."""
    
    with open("admin_policy.txt", "w", encoding="utf-8") as f:
        f.write(policy_content)
        
    # Create messy CSV logs
    # Prof. Adams: 20 Teaching, 15 Research, 5 Admin (Total 40, Admin 12.5% -> Compliant)
    # Prof. Barnes: 15 Teaching, 10 Research, 15 Admin (Total 40, Admin 37.5% -> VIOLATOR)
    # Prof. Chen: 10 Teaching, 20 Research, 2 Admin (Total 32, Admin 6.25% -> Compliant)
    # Prof. Davis: 10 Teaching, 10 Research, 10 Admin (Total 30, Admin 33.3% -> VIOLATOR)
    
    log1_data = [
        ["Name", "Teaching_Hours", "Research_Hours", "Admin_Hours"],
        ["Adams", "20", "15", "5  "],
        [" Barnes ", "15", "10", "15"]
    ]
    
    log2_data = [
        ["Full Name", "Teaching", "Research", "Admin"],
        ["Chen", "10", "20", "2"],
        ["Davis", "10", "10", "10"]
    ]
    
    with open("raw_data/faculty_logs/week1.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(log1_data)
        
    with open("raw_data/faculty_logs/week2_alt_format.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(log2_data)

if __name__ == "__main__":
    build_env()
