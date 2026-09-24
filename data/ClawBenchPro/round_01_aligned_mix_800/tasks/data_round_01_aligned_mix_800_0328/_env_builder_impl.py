import os
import json

def build_env():
    # Create the applications directory
    apps_dir = "applications"
    os.makedirs(apps_dir, exist_ok=True)
    
    # Client data - Note the changes: .dat files and encoded hashes
    clients = [
        {"id": "A101", "name": "John Miller", "hobbies": ["Reading", "Golf"], "encoded_id_hash": "hash_jm_2"},
        {"id": "A102", "name": "Alice Vance", "hobbies": ["Skydiving", "Painting"], "encoded_id_hash": "hash_av_0"},
        {"id": "A103", "name": "Bob Harrison", "hobbies": ["Rock Climbing"], "encoded_id_hash": "hash_bh_3"},
        {"id": "A104", "name": "Charlie Dunn", "hobbies": ["Scuba Diving"], "encoded_id_hash": "hash_cd_1"},
        {"id": "A105", "name": "Diana Prince", "hobbies": ["Hiking", "Tennis"], "encoded_id_hash": "hash_dp_4"},
        {"id": "A106", "name": "Edward Norton", "hobbies": ["Gardening"], "encoded_id_hash": "hash_en_0"}
    ]
    
    # Write client data to individual .dat files (simulating a proprietary format)
    for client in clients:
        file_path = os.path.join(apps_dir, f"app_{client['id']}.dat")
        with open(file_path, 'w') as f:
            # We use JSON format inside but with .dat extension to force the Agent to inspect
            json.dump(client, f, indent=4)
            
    # Add dirty data
    with open(os.path.join(apps_dir, "config.ini"), 'w') as f:
        f.write("[System]\nMode=ActuaryV3")
    
    # Create the target directory placeholder
    os.makedirs("policy_sorting", exist_ok=True)

if __name__ == "__main__":
    build_env()
