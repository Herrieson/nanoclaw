import os
import json

def build_env():
    base_dir = "assets/data_34"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Visitor Center
    with open(os.path.join(base_dir, "visitor_center.txt"), "w") as f:
        f.write("39.1031, -84.5120\n")

    # 2. Waypoints CSV
    waypoints = """id,lat,lon
1,39.1050,-84.5100
2,39.1100,-84.5000
3,39.1200,-84.4800
4,39.1300,-84.4500
5,39.1500,-84.4000
6,39.1400,-84.4200
"""
    with open(os.path.join(base_dir, "waypoints.csv"), "w") as f:
        f.write(waypoints)

    # 3. Eco Zones JSON
    eco_zones = [
        {"min_lat": 39.109, "max_lat": 39.115, "min_lon": -84.505, "max_lon": -84.495},
        {"min_lat": 39.125, "max_lat": 39.135, "min_lon": -84.455, "max_lon": -84.445}
    ]
    with open(os.path.join(base_dir, "eco_zones.json"), "w") as f:
        json.dump(eco_zones, f, indent=2)

    # 4. History Notes
    notes = """ID: 1 - The first settlement outpost.
ID: 2 - Nesting grounds (should be skipped).
ID: 3 - Historic battle site.
ID: 4 - Old river ford.
ID: 5 - Pioneer cabin ruins.
ID: 6 - Trading post remains.
"""
    with open(os.path.join(base_dir, "history_notes.txt"), "w") as f:
        f.write(notes)

if __name__ == "__main__":
    build_env()
