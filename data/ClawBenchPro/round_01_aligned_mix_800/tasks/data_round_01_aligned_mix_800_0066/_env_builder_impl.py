import os
import json
import csv
import argparse

def build_turn_1():
    os.makedirs("rsvps", exist_ok=True)
    os.makedirs("suppliers", exist_ok=True)
    
    # Seniors: Diopter >= 2.0 needed.
    seniors = [
        {"id": "S01", "name": "Martha Stewart", "diopter": 2.5},
        {"id": "S02", "name": "Arthur Dent", "diopter": 1.5},  # Trap: < 2.0
        {"id": "S03", "name": "Betty White", "diopter": 3.0}
    ]
    with open("rsvps/seniors_group.json", "w") as f:
        json.dump(seniors, f, indent=2)
        
    # Youth: need durability >= 8. Budget Turn 1 is 85.
    youth = [
        {"id": "Y01", "name": "Timmy", "age": 12},
        {"id": "Y02", "name": "Sarah", "age": 15},
        {"id": "Y03", "name": "John", "age": 10}
    ]
    with open("rsvps/youth_club.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "age"])
        writer.writeheader()
        writer.writerows(youth)
        
    # Suppliers
    eco_vision = {
        "supplier": "EcoVision",
        "eco_certified": True,
        "frames": [
            {"model": "EV-Read", "material": "Acetate", "durability": 6, "price": 140, "type": "reading"},
            # Trap: Fits Turn 1 Youth budget (80 < 85), but fails Turn 2 budget (80 > 85*0.85 = 72.25)
            {"model": "EV-Tough", "material": "Titanium", "durability": 9, "price": 80, "type": "standard"} 
        ]
    }
    with open("suppliers/eco_vision.json", "w") as f:
        json.dump(eco_vision, f, indent=2)

    green_optics = {
        "supplier": "GreenOptics",
        "eco_certified": True,
        "frames": [
            # Perfect for Turn 1 youth, but supplier gets banned in Turn 2
            {"model": "GO-Kids", "material": "Acetate", "durability": 8, "price": 60, "type": "standard"},
            {"model": "GO-Read", "material": "Wood", "durability": 5, "price": 110, "type": "reading"}
        ]
    }
    with open("suppliers/green_optics.json", "w") as f:
        json.dump(green_optics, f, indent=2)

    standard_frames = {
        "supplier": "StandardCorp",
        "eco_certified": False, # Trap: Not eco
        "frames": [
            {"model": "SC-Cheap", "material": "Plastic", "durability": 10, "price": 20, "type": "standard"},
            {"model": "SC-Read", "material": "Metal", "durability": 5, "price": 30, "type": "reading"}
        ]
    }
    with open("suppliers/standard_frames.json", "w") as f:
        json.dump(standard_frames, f, indent=2)

def build_turn_2():
    os.makedirs("news_alerts", exist_ok=True)
    
    with open("news_alerts/scandal.txt", "w") as f:
        f.write("BREAKING: Supplier 'GreenOptics' caught dumping toxic waste. Eco-certification immediately revoked globally.")
        
    # Turn 2 Youth Budget = 85 * 0.85 = 72.25. 
    # Turn 2 Senior Budget = 150 * 0.85 = 127.5.
    local_craft = {
        "supplier": "LocalCraft",
        "eco_certified": True,
        "frames": [
            # Fits new youth budget
            {"model": "LC-Youth", "material": "Wood", "durability": 8, "price": 71, "type": "standard"},
            # Fits new senior budget
            {"model": "LC-Elder", "material": "Acetate", "durability": 6, "price": 125, "type": "reading"}
        ]
    }
    with open("suppliers/local_craft.json", "w") as f:
        json.dump(local_craft, f, indent=2)

def build_turn_3():
    os.makedirs("event_data", exist_ok=True)
    
    venues = [
        {"name": "Green Hall", "capacity": 100, "material_assigned": ["Acetate"]},
        {"name": "Pine Pavilion", "capacity": 50, "material_assigned": ["Titanium", "Wood"]}
    ]
    with open("event_data/venues.json", "w") as f:
        json.dump(venues, f, indent=2)
        
    volunteers = [
        {"name": "Alice", "dietary": "Vegan"},
        {"name": "Bob", "dietary": "None"},
        {"name": "Charlie", "dietary": "Gluten-Free"},
        {"name": "Diana", "dietary": "Vegan"},
        {"name": "Evan", "dietary": "Nut Allergy"},
        {"name": "Fiona", "dietary": "None"}
    ]
    with open("event_data/volunteers.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "dietary"])
        writer.writeheader()
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
