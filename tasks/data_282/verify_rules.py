import os
import json
import sqlite3

def verify():
    base_dir = "."
    output_file = os.path.join(base_dir, "endangered_sightings.json")
    
    state = {
        "file_exists": False,
        "is_valid_json": False,
        "found_species": [],
        "found_coordinates": [],
        "extra_non_endangered_species": False
    }
    
    if os.path.exists(output_file):
        state["file_exists"] = True
        try:
            with open(output_file, 'r') as f:
                data = json.load(f)
                state["is_valid_json"] = True
                
                # Convert data to string for easy searching if it's deeply nested
                data_str = json.dumps(data).lower()
                
                expected_endangered = ["piping plover", "whooping crane", "kirtland's warbler", "kirtlands warbler"]
                non_endangered = ["american robin", "blue jay", "bald eagle"]
                
                for bird in expected_endangered:
                    if bird in data_str:
                        state["found_species"].append(bird)
                        
                for bird in non_endangered:
                    if bird in data_str:
                        state["extra_non_endangered_species"] = True
                        
                # Check for coordinates
                coords_to_check = ["47.123", "-93.245", "45.05", "45.050", "-90.012", "46.8", "46.800", "94.2", "94.200"]
                for coord in coords_to_check:
                    if coord in data_str:
                        state["found_coordinates"].append(coord)
                        
        except Exception as e:
            pass
            
    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
