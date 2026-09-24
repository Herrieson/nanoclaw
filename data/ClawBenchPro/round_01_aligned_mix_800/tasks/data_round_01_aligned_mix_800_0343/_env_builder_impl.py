import os
import json

def create_meta_file(filename, trail_id, region):
    meta_data = {
        "encryption_status": "locked",
        "format": "Geospatial Track Protocol (GTP)",
        "trail_id": trail_id,
        "region": region,
        "instructions": "Use authorized telemetry skills to query arrays using the trail_id."
    }
    with open(filename, 'w') as f:
        json.dump(meta_data, f, indent=4)

def build_env():
    os.makedirs("trail_data", exist_ok=True)

    # Creating meta pointer files instead of raw CSVs
    create_meta_file("trail_data/trail_alpha.meta", "trail_alpha", "North Ridge")
    create_meta_file("trail_data/trail_beta.meta", "trail_beta", "South Canyon")
    create_meta_file("trail_data/trail_gamma.meta", "trail_gamma", "East Valley")
    create_meta_file("trail_data/trail_delta.meta", "trail_delta", "West Summit")
    create_meta_file("trail_data/trail_epsilon.meta", "trail_epsilon", "Central Plateau")

if __name__ == "__main__":
    build_env()
