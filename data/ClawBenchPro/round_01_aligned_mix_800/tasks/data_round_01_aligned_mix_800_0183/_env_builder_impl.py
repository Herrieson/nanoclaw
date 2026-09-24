import os
import json
import csv
import xml.etree.ElementTree as ET
import argparse

def build_turn_1():
    os.makedirs("data/vendors", exist_ok=True)
    os.makedirs("data/volunteers", exist_ok=True)
    os.makedirs("results", exist_ok=True)
    
    vendors = [
        {
            "vendor_id": "V101",
            "category": "Vegan-Food",
            "eco_metrics": {"plastic_free": True, "certifications_count": 2},
            "employment": {"hourly_wage": 16.5},
            "needs": {"shift": "Morning", "role": "Setup"}
        },
        {
            "vendor_id": "V102",
            "category": "Fast-Food",
            "eco_metrics": {"plastic_free": False, "certifications_count": 5},
            "employment": {"hourly_wage": 20.0},
            "needs": {"shift": "Morning", "role": "Setup"}
        },
        {
            "vendor_id": "V103",
            "category": "Crafts",
            "eco_metrics": {"plastic_free": True, "certifications_count": 3},
            "employment": {"hourly_wage": 15.0},
            "needs": {"shift": "Afternoon", "role": "Cleanup"}
        },
        {
            "vendor_id": "V104",
            "category": "Eco-Art",
            "eco_metrics": {"plastic_free": True, "certifications_count": 4},
            "employment": {"hourly_wage": 18.0},
            "needs": {"shift": "Afternoon", "role": "Cleanup"}
        },
        {
            "vendor_id": "V105",
            "category": "Tech",
            "eco_metrics": {"plastic_free": True, "certifications_count": 1},
            "employment": {"hourly_wage": 25.0},
            "needs": {"shift": "Evening", "role": "Security"}
        },
        {
            "vendor_id": "V106",
            "category": "Renewable-Tech",
            "eco_metrics": {"plastic_free": True, "certifications_count": 2},
            "employment": {"hourly_wage": 16.0},
            "needs": {"shift": "Evening", "role": "Security"}
        }
    ]
    
    with open("data/vendors/initial_batch.json", "w") as f:
        json.dump(vendors, f, indent=2)
        
    volunteers = [
        {"name": "Alice", "shift_pref": "Morning", "skill": "Setup"},
        {"name": "Bob", "shift_pref": "Morning", "skill": "Setup"},
        {"name": "Charlie", "shift_pref": "Morning", "skill": "Setup"},
        {"name": "Diana", "shift_pref": "Afternoon", "skill": "Cleanup"},
        {"name": "Eve", "shift_pref": "Afternoon", "skill": "Cleanup"},
        {"name": "Finn", "shift_pref": "Afternoon", "skill": "Cleanup"},
        {"name": "Henry", "shift_pref": "Evening", "skill": "Security"},
        {"name": "Ivy", "shift_pref": "Evening", "skill": "Security"},
        {"name": "Jack", "shift_pref": "Evening", "skill": "Security"},
        {"name": "Liam", "shift_pref": "Morning", "skill": "Greeter"},
        {"name": "Grace", "shift_pref": "Morning", "skill": "Greeter"},
        {"name": "John", "shift_pref": "Morning", "skill": "Greeter"}
    ]
    
    with open("data/volunteers/signups.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["name", "shift_pref", "skill"])
        writer.writeheader()
        writer.writerows(volunteers)

def build_turn_2():
    os.makedirs("data/vendors", exist_ok=True)
    os.makedirs("data/drama", exist_ok=True)
    
    root = ET.Element("vendors")
    
    # V201: Passes all strict rules from Turn 1
    v1 = ET.SubElement(root, "vendor", id="V201")
    ET.SubElement(v1, "category").text = "Organic-Skincare"
    ET.SubElement(v1, "metrics", plastic_free="true", certs="3")
    ET.SubElement(v1, "pay", wage="17.0")
    ET.SubElement(v1, "requirements", shift="Morning", role="Greeter")
    
    # V202: Fails wage rule (15.5)
    v2 = ET.SubElement(root, "vendor", id="V202")
    ET.SubElement(v2, "category").text = "Handmade-Jewelry"
    ET.SubElement(v2, "metrics", plastic_free="true", certs="2")
    ET.SubElement(v2, "pay", wage="15.5")
    ET.SubElement(v2, "requirements", shift="Morning", role="Greeter")

    tree = ET.ElementTree(root)
    tree.write("data/vendors/late_applications.xml")
    
    dropout_text = "Yo, this weather is brick! I'm officially dropping out, sorry - Alice.\nP.S. I saw Grace at Wawa earlier and she said she's also bailing because she has to work."
    with open("data/drama/dropouts.txt", "w") as f:
        f.write(dropout_text)

def build_turn_3():
    os.makedirs("data/sponsor", exist_ok=True)
    rules = {
        "target_categories": ["Vegan-Food", "Eco-Art", "Renewable-Tech", "Organic-Skincare"],
        "grant_per_vendor": 500
    }
    with open("data/sponsor/green_ocean_rules.json", "w") as f:
        json.dump(rules, f, indent=2)

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
