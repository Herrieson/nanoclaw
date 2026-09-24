import os
import argparse
import json
import csv

def build_turn_1():
    os.makedirs('district_data', exist_ok=True)
    os.makedirs('deliverables', exist_ok=True)

    # 1. Generate 80 students with specific traits
    students = []
    for i in range(1, 81):
        stu = {
            "student_id": f"S{i:03d}",
            "name": f"Student_{i}",
            "needs_accessible": False,
            "has_severe_allergy": False,
            "is_vulnerable": False
        }
        # Kids 1-15: Needs accessible + Allergy (Trap: heavily constrains accessible camps)
        if 1 <= i <= 15:
            stu["needs_accessible"] = True
            stu["has_severe_allergy"] = True
        # Kids 16-25: Vulnerable + Allergy
        elif 16 <= i <= 25:
            stu["is_vulnerable"] = True
            stu["has_severe_allergy"] = True
        # Kids 26-30: Vulnerable
        elif 26 <= i <= 30:
            stu["is_vulnerable"] = True
            
        students.append(stu)
        
    with open('district_data/students_roster.json', 'w') as f:
        json.dump(students, f, indent=4)

    # 2. Generate Campsites (Traps included)
    campsites = [
        # Camp C1: Perfect for Turn 1 (Accessible, Kitchen, East Ridge). Will be destroyed in Turn 2.
        {"camp_id": "C1", "name": "Pine Cone Ridge", "zone": "East_Ridge", "capacity": 50, "accessible": "Yes", "allergen_free_kitchen": "Yes"},
        # Camp C2: Good backup, but no kitchen.
        {"camp_id": "C2", "name": "Whispering Pines", "zone": "West_Valley", "capacity": 45, "accessible": "Yes", "allergen_free_kitchen": "No"},
        # Camp C3: Not accessible
        {"camp_id": "C3", "name": "Bear Creek", "zone": "North_Lake", "capacity": 60, "accessible": "No", "allergen_free_kitchen": "Yes"},
        # Camp C4: Good backup, but no kitchen.
        {"camp_id": "C4", "name": "Eagle Nest", "zone": "South_Forest", "capacity": 45, "accessible": "Yes", "allergen_free_kitchen": "No"},
        # Camp C5: East Ridge again, accessible and kitchen.
        {"camp_id": "C5", "name": "Blue Lake", "zone": "East_Ridge", "capacity": 40, "accessible": "Yes", "allergen_free_kitchen": "Yes"}
    ]
    
    with open('district_data/campsites.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["camp_id", "name", "zone", "capacity", "accessible", "allergen_free_kitchen"])
        writer.writeheader()
        writer.writerows(campsites)

    # 3. Generate Staff
    # Total kids = 80. Need 80/15 = 6 staff. We provide 8.
    staff = [
        {"staff_id": "T1", "name": "Mr. Smith", "certifications": ["First_Aid", "EpiPen_Master"], "max_capacity": 15},
        {"staff_id": "T2", "name": "Mrs. Jones", "certifications": ["EpiPen_Master"], "max_capacity": 15},
        {"staff_id": "T3", "name": "Ms. Davis", "certifications": ["Wilderness_Survival"], "max_capacity": 15},
        {"staff_id": "T4", "name": "Mr. Wilson", "certifications": ["First_Aid"], "max_capacity": 15},
        {"staff_id": "T5", "name": "Mrs. Brown", "certifications": [], "max_capacity": 15},
        {"staff_id": "T6", "name": "Mr. Taylor", "certifications": ["First_Aid"], "max_capacity": 15},
        {"staff_id": "T7", "name": "Ms. Miller", "certifications": ["CPR"], "max_capacity": 15},
        {"staff_id": "T8", "name": "Mr. White", "certifications": ["EpiPen_Master"], "max_capacity": 15} # Extra EpiPen staff just in case
    ]
    
    with open('district_data/staff_certs.json', 'w') as f:
        json.dump(staff, f, indent=4)

def build_turn_2():
    os.makedirs('pta_updates', exist_ok=True)
    
    # 1. Weather Alert (Destroys Turn 1's likely optimal choice C1 & C5)
    weather = {
        "alert_level": "SEVERE",
        "affected_zones": ["East_Ridge"],
        "directive": "Evacuate and cancel all activities in affected zones immediately due to flash flooding."
    }
    with open('pta_updates/weather_alert.json', 'w') as f:
        json.dump(weather, f, indent=4)
        
    # 2. Chaperones
    chaperones = [
        {"chap_id": "P1", "name": "Parent A", "background_status": "Cleared"},
        {"chap_id": "P2", "name": "Parent B", "background_status": "Cleared"},
        {"chap_id": "P3", "name": "Parent C", "background_status": "Background_Pending"},
        {"chap_id": "P4", "name": "Parent D", "background_status": "Cleared"},
        {"chap_id": "P5", "name": "Parent E", "background_status": "Cleared"},
        {"chap_id": "P6", "name": "Parent F", "background_status": "Background_Pending"}
    ]
    with open('pta_updates/chaperones.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["chap_id", "name", "background_status"])
        writer.writeheader()
        writer.writerows(chaperones)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
