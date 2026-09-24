import sys
import json

def analyze_material(description):
    mapping = {
        "recycled organic acetate": {"brand": "WoodSpecs", "is_eco_friendly": True},
        "recycled ocean-bound plastic": {"brand": "OceanPlastics Co.", "is_eco_friendly": True},
        "standard petroleum plastic": {"brand": "Generic Junk", "is_eco_friendly": False},
        "cheap brittle resin": {"brand": "Generic Junk", "is_eco_friendly": False}
    }
    desc_lower = description.lower()
    return json.dumps(mapping.get(desc_lower, {"brand": "Unknown", "is_eco_friendly": False}))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(analyze_material(sys.argv[1]))
