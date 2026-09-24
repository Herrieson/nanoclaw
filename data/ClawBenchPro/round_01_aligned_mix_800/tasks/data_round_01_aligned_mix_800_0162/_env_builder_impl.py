import os
import argparse
import json
import csv

def build_turn_1():
    os.makedirs("policies", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("workspace", exist_ok=True)

    # 1. Budget Rules
    rules = """ECO-FAIR 2024 OFFICIAL GUIDELINES

1. **Total Event Budget**: $8,500. We must not exceed this under any circumstances.
2. **Project Quota**: We must select EXACTLY 5 student projects to showcase. No more, no less.
3. **Project Cap**: The maximum allowable cost per project (student base materials + vendor service fee) is $1,500.
4. **Allowed Categories**: Composting, Solar, Upcycling, Urban Farming.
5. **Vendor Eligibility**: All vendors MUST have `green_certification` set to True.
"""
    with open("policies/budget_rules.md", "w", encoding="utf-8") as f:
        f.write(rules)

    # 2. Student Batch 1
    students = [
        {"project_id": "P01", "student_group": "Grade 5 Earth Savers", "category": "Composting", "base_materials_cost": 400},
        {"project_id": "P02", "student_group": "Sun Catchers", "category": "Solar", "base_materials_cost": 600},
        {"project_id": "P03", "student_group": "Plastic Reborn", "category": "Upcycling", "base_materials_cost": 300}, # Trap: pairs well with EcoPlastics
        {"project_id": "P04", "student_group": "City Sprouts", "category": "Urban Farming", "base_materials_cost": 500},
        {"project_id": "P05", "student_group": "Worm Whisperers", "category": "Composting", "base_materials_cost": 800},
        {"project_id": "P06", "student_group": "Mecha Minds", "category": "Robotics", "base_materials_cost": 200}, # Invalid category
        {"project_id": "P07", "student_group": "Solar Flares", "category": "Solar", "base_materials_cost": 1200}  # Likely to break $1500 cap
    ]
    with open("data/students_batch1.json", "w", encoding="utf-8") as f:
        json.dump(students, f, indent=4)

    # 3. Vendor Catalog
    vendors = [
        ["vendor_name", "focus_area", "service_fee", "green_certification"],
        ["GreenEarth", "Composting", 500, "True"],
        ["SunPower", "Solar", 600, "True"], # Trap for Turn 2
        ["EcoPlastics Inc.", "Upcycling", 200, "True"], # Trap for Turn 2
        ["CityRoots", "Urban Farming", 700, "True"],
        ["DirtCheap", "Composting", 100, "False"],
        ["Trash2Treasure", "Upcycling", 800, "True"],
        ["SolarTech Solutions", "Solar", 800, "True"]
    ]
    with open("data/vendors_catalog.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(vendors)

def build_turn_2():
    os.makedirs("news", exist_ok=True)
    
    # 1. Vendor Audit News
    audit_news = """URGENT INVESTIGATIVE REPORT: LOCAL GREENWASHING SCANDAL EXPOSED

This morning, the Environmental Protection Board announced the immediate revocation of green certifications for several prominent local businesses found guilty of illegal waste dumping and falsifying emissions data.

Effective immediately, the following businesses are no longer green certified:
- EcoPlastics Inc.
- SunPower
- GlobalGreen Corp.
"""
    with open("news/vendor_audit.txt", "w", encoding="utf-8") as f:
        f.write(audit_news)

    # 2. Student Batch 2 (Late submissions)
    batch2 = [
        {"project_id": "P08", "student_group": "Light Harvesters", "category": "Solar", "base_materials_cost": 400},
        {"project_id": "P09", "student_group": "Trash Transformers", "category": "Upcycling", "base_materials_cost": 500},
        {"project_id": "P10", "student_group": "Rooftop Radishes", "category": "Urban Farming", "base_materials_cost": 300}
    ]
    with open("data/students_batch2.json", "w", encoding="utf-8") as f:
        json.dump(batch2, f, indent=4)

def build_turn_3():
    # 1. Volunteers Data
    volunteers = [
        ["name", "age", "skill"],
        ["Alice Walker", 35, "Soil Prep"],
        ["Bobby Tables", 16, "Waste Sorting"],
        ["Charlie Davis", 42, "Electrical"],
        ["Diana Prince", 28, "Crafting"],
        ["Evan Wright", 15, "Gardening"],
        ["Fiona Gallagher", 22, "Waste Sorting"],
        ["George Miller", 17, "Engineering"],
        ["Hannah Abbott", 19, "Soil Prep"],
        ["Ian Malcolm", 45, "Engineering"],
        ["Jessica Jones", 30, "Crafting"],
        ["Kevin Hart", 16, "Electrical"],
        ["Laura Palmer", 25, "Gardening"]
    ]
    with open("data/volunteers.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(volunteers)

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
