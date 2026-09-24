import os
import argparse
import csv
import json

def build_turn_1():
    os.makedirs("vendors", exist_ok=True)
    os.makedirs("festival_rules", exist_ok=True)

    # Catalog A (CSV)
    catalog_a_data = [
        ["id", "name", "origin", "cultural_score", "price", "sunlight", "weight_kg", "size_sqft", "type"],
        ["A01", "Pioneer Wagon Wheel", "Oklahoma Native", "85", "300", "none", "45", "15", "artifact"],
        ["A02", "Dust Bowl Plow", "Oklahoma Native", "70", "150", "none", "60", "20", "artifact"],
        ["A03", "Celtic Stone Cross", "Dublin_Shipment", "95", "120", "none", "80", "10", "artifact"], # Poison pill for turn 2
        ["A04", "Galway Wool Loom", "Irish", "80", "400", "none", "35", "12", "artifact"],
        ["A05", "Prairie Sunflower Seedlings", "Oklahoma Native", "50", "40", "full_sun", "5", "4", "plant"],
        ["A06", "Shamrock Bed", "Irish", "60", "60", "partial_shade", "8", "6", "plant"],
        ["A07", "Victorian Tea Set", "London", "40", "200", "none", "10", "5", "artifact"]
    ]
    with open("vendors/catalog_A.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(catalog_a_data)

    # Catalog B (JSON)
    catalog_b_data = [
        {
            "item_id": "B01", "title": "Belfast Harp Replica", "source": "Irish", 
            "heritage_rating": 90, "cost": 450, "maintenance": "none", "mass_kg": 25, "area_sqft": 8, "category": "artifact"
        },
        {
            "item_id": "B02", "title": "Native Pecan Tree Sapling", "source": "Oklahoma Native", 
            "heritage_rating": 75, "cost": 90, "maintenance": "full_sun", "mass_kg": 15, "area_sqft": 10, "category": "plant"
        },
        {
            "item_id": "B03", "title": "Wild Onion Basket", "source": "Oklahoma Native", 
            "heritage_rating": 65, "cost": 50, "maintenance": "partial_shade", "mass_kg": 3, "area_sqft": 2, "category": "plant"
        },
        {
            "item_id": "B04", "title": "Connemara Marble Bench", "source": "West_Coast_Port", 
            "heritage_rating": 88, "cost": 250, "maintenance": "full_sun", "mass_kg": 120, "area_sqft": 18, "category": "artifact"
        }, # Another poison pill
        {
            "item_id": "B05", "title": "Killarney Ferns", "source": "Irish", 
            "heritage_rating": 55, "cost": 75, "maintenance": "partial_shade", "mass_kg": 12, "area_sqft": 8, "category": "plant"
        }
    ]
    with open("vendors/catalog_B.json", "w") as f:
        json.dump(catalog_b_data, f, indent=4)

    # Constraints
    constraints_content = """FESTIVAL PURCHASING RULES:
1. Total Budget: Maximum $900.
2. Heritage Standard: The sum of the cultural/heritage scores of all purchased items MUST be strictly greater than 350.
3. Origin Quotas:
   - Must include AT LEAST 2 items from "Irish" or "Dublin_Shipment" or "West_Coast_Port".
   - Must include AT LEAST 2 items from "Oklahoma Native".
4. Variety: Must purchase at least 5 items in total.
Note: Be frugal but ensure we hit these numbers exactly!
"""
    with open("festival_rules/constraints.txt", "w") as f:
        f.write(constraints_content)


def build_turn_2():
    os.makedirs("updates", exist_ok=True)
    os.makedirs("volunteers", exist_ok=True)

    # Shipping delays
    delays_content = """URGENT LOGISTICS ALERT:
Due to a major dockworkers strike, all items with the following origins are indefinitely delayed and cannot be purchased:
- Dublin_Shipment
- West_Coast_Port
Please revise all plans immediately to exclude items from these sources.
"""
    with open("updates/shipping_delays.txt", "w") as f:
        f.write(delays_content)

    # Volunteers
    volunteers_data = [
        ["name", "age", "can_lift_heavy"],
        ["John", "34", "yes"],
        ["Mike", "17", "yes"], # Underage, cannot be assigned to heavy
        ["Sarah", "29", "no"],
        ["David", "45", "yes"],
        ["Emma", "22", "yes"],
        ["Chris", "19", "no"],
        ["Liam", "25", "yes"],
        ["Chloe", "31", "yes"]
    ]
    with open("volunteers/roster.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(volunteers_data)


def build_turn_3():
    os.makedirs("venues", exist_ok=True)
    
    # Venue Map
    venue_map = {
        "zones": [
            {
                "zone_id": "Z1",
                "name": "Sunny Heritage Plaza",
                "sunlight": "full_sun",
                "capacity_sqft": 40
            },
            {
                "zone_id": "Z2",
                "name": "Shaded Grove",
                "sunlight": "partial_shade",
                "capacity_sqft": 30
            },
            {
                "zone_id": "Z3",
                "name": "Indoor Artifact Hall A",
                "sunlight": "none",
                "capacity_sqft": 50
            },
            {
                "zone_id": "Z4",
                "name": "Indoor Artifact Hall B",
                "sunlight": "none",
                "capacity_sqft": 40
            }
        ]
    }
    with open("venues/map.json", "w") as f:
        json.dump(venue_map, f, indent=4)


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
