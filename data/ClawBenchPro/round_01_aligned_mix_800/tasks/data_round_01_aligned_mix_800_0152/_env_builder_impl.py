import os
import argparse
import json
import csv

def build_turn_1():
    os.makedirs("blueprints", exist_ok=True)
    os.makedirs("parish_guidelines", exist_ok=True)
    os.makedirs("suppliers", exist_ok=True)

    # Blueprints
    specs = """PAVILION BLUEPRINTS v1.0
Footprint: 10ft x 10ft
Required Structural Components:
- Corner Posts: 4 units, required length: 10ft. Minimum tensile strength: 40 MPa.
- Roof Beams: 10 units, required length: 12ft. Minimum tensile strength: 60 MPa.
- Decking: 100 square feet. Minimum tensile strength: 30 MPa.
"""
    with open("blueprints/specs.txt", "w") as f:
        f.write(specs)

    # Parish Rules
    rules = {
        "total_project_budget_usd": 8500,
        "aesthetic_rules": {
            "forbidden_materials": [
                "chemically treated pine (toxic)",
                "tropical hardwoods unless explicitly marked as FSC Certified"
            ],
            "finish": "natural"
        }
    }
    with open("parish_guidelines/rules.json", "w") as f:
        json.dump(rules, f, indent=4)

    # Supplier Catalog
    catalog = [
        ["supplier_id", "species", "origin", "is_fsc_certified", "tensile_strength_mpa", "available_lengths_ft", "price_per_ft_usd", "decking_price_per_sqft_usd", "contact"],
        # Trap 1: Cheap, strong enough, but tropical and NOT FSC certified
        ["S101", "Honduran Mahogany", "Tropical", "No", "75", "10,12,14,16", "12", "18", "bob@mahagony.com"],
        # Trap 2: Domestic, cheap, but too weak for roof beams (45 < 60) and chemically treated
        ["S102", "Treated Pine", "Domestic", "Yes", "45", "10,12,14", "6", "10", "sales@pinewood.com"],
        # Valid 1: Strong, FSC certified, but only goes up to 12ft lengths (Will be a problem in Turn 2)
        ["S103", "Brazilian Walnut", "Tropical", "Yes", "110", "10,12", "16", "22", "import@walnut.com"],
        # Valid 2: Domestic, strong, long lengths available, but expensive.
        ["S104", "White Oak", "Domestic", "Yes", "90", "10,12,14,16", "24", "28", "contact@oakmasters.com"]
    ]
    with open("suppliers/wood_catalog.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(catalog)

def build_turn_2():
    os.makedirs("updates", exist_ok=True)
    
    notes = """Liam,
I had a vision last night! The pavilion must be grander. Please expand the footprint to 12ft x 12ft.
This means the Corner Posts stay at 10ft tall, but the Roof Beams must now be 14ft long! The decking will also increase to 144 square feet.
Also, Mrs. Higgins donated $500, but ONLY if we use Iron Cross Brackets for the joints. I've left the bracket catalog. 
Blessings,
Father Thomas
"""
    with open("updates/father_thomas_notes.txt", "w") as f:
        f.write(notes)

    decor = [
        ["bracket_id", "name", "wood_compatibility", "price_per_unit"],
        ["B1", "Iron Cross Bracket", "White Oak, Red Oak, Cedar", "25"],
        ["B2", "Copper Bracket", "Walnut, Mahogany, Teak", "40"]
    ]
    # Note: 14 roof beams + 4 corner posts = 18 joints? We don't specify quantities of brackets needed in detail, 
    # but the primary trap is the wood compatibility and the 14ft length requirement.
    # If they chose Brazilian Walnut in Turn 1, it's incompatible with Iron Cross AND doesn't sell 14ft lengths.
    with open("suppliers/decor.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(decor)

def build_turn_3():
    os.makedirs("deliveries", exist_ok=True)
    os.makedirs("manuals", exist_ok=True)

    inspection = """INSPECTION LOG:
Total Roof Beams ordered (14ft): 10
Damaged: 4 of the roof beams have severe warping on one end.
I measured them: we can only get exactly 9 feet of usable, straight wood out of each of those 4 warped beams. 
We need them to be 14 feet long! We have to cut off the bad parts and splice on new pieces.
"""
    with open("deliveries/inspection.txt", "w") as f:
        f.write(inspection)

    manual = {
        "Scarf Joint": {
            "description": "A traditional end-to-end splice.",
            "required_overlap_ft": 2.0,
            "strength_retention_percent": 85,
            "suitable_for_min_mpa": 50
        },
        "Spline Joint": {
            "description": "Hidden internal spline.",
            "required_overlap_ft": 1.0,
            "strength_retention_percent": 50,
            "suitable_for_min_mpa": 30
        }
    }
    # If original requirement was 60 MPa, White oak is 90 MPa. 
    # Scarf Joint retention = 90 * 0.85 = 76.5 MPa (Passes 60 MPa requirement).
    # Spline Joint retention = 90 * 0.50 = 45 MPa (Fails 60 MPa requirement).
    # So they MUST choose Scarf Joint.
    # Math: Need 14ft total. Have 9ft usable. Gap = 5ft.
    # Because Scarf Joint requires 2ft overlap, the replacement splice piece must be: Gap (5) + Overlap (2) = 7ft long.
    with open("manuals/joinery_hacks.json", "w") as f:
        json.dump(manual, f, indent=4)


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
