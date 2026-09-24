import os
import json

def build_env():
    # Create directories
    os.makedirs("raw_data/faculty_logs", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    
    # Create the policy file with the new weight factor
    policy_content = """UNIVERSITY PROCEDURAL GUIDELINE - TIME ALLOCATION (REVISED)
As per state funding mandates and university efficiency protocols, faculty members must prioritize Teaching and Research. 
Under no circumstances should 'Administrative' duties exceed 20% of a faculty member's total logged hours.

AUDIT RULE: For all efficiency studies, a 'Complexity Multiplier' of 1.1x must be applied to all self-reported Administrative hours before calculating the percentage.
Total Hours = Teaching + Research + (Admin * 1.1)
Administrative Percentage = (Admin * 1.1) / Total Hours

Violators will be subject to a workload audit."""
    
    with open("admin_policy.txt", "w", encoding="utf-8") as f:
        f.write(policy_content)
        
    # Create the "Encrypted" .dat file content (Internal representation for the Skill to mock)
    # Data Plan:
    # Prof. Adams: T:20, R:15, A:5  => (5*1.1)/(20+15+5.5) = 5.5/40.5 = 13.5% (Compliant)
    # Prof. Barnes: T:15, R:10, A:10 => (10*1.1)/(15+10+11) = 11/36 = 30.5% (VIOLATOR)
    # Prof. Chen:  T:10, R:20, A:2  => (2.2)/(10+20+2.2) = 2.2/32.2 = 6.8% (Compliant)
    # Prof. Davis: T:10, R:10, A:6  => (6.6)/(10+10+6.6) = 6.6/26.6 = 24.8% (VIOLATOR)
    
    mock_db_content = {
        "records": [
            {"name": "Adams", "teaching": 20, "research": 15, "admin": 5},
            {"name": "Barnes", "teaching": 15, "research": 10, "admin": 10},
            {"name": "Chen", "teaching": 10, "research": 20, "admin": 2},
            {"name": "Davis", "teaching": 10, "research": 10, "admin": 6}
        ]
    }
    
    with open("raw_data/faculty_logs/logs_archived.dat", "w", encoding="utf-8") as f:
        f.write("--- ENCRYPTED UNIVERSITY DATA ---\n")
        f.write(json.dumps(mock_db_content))
        f.write("\n--- END OF BUFFER ---")

    # Create a placeholder for the PDF
    with open("raw_data/faculty_logs/additional_notes.pdf", "w", encoding="utf-8") as f:
        f.write("PDF Content Placeholder: Use pdf_extractor_skill to read this file.")

if __name__ == "__main__":
    build_env()
