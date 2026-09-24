import os
import json

def build_env():
    # Create the applications directory in the current working directory
    apps_dir = "applications"
    os.makedirs(apps_dir, exist_ok=True)
    
    # Client data
    clients = [
        {
            "id": "A101",
            "name": "John Miller",
            "age": 42,
            "marital_status": "Married",
            "children": 2,
            "hobbies": ["Reading", "Golf", "Cooking"],
            "income": 85000
        },
        {
            "id": "A102",
            "name": "Alice Vance",
            "age": 28,
            "marital_status": "Single",
            "children": 0,
            "hobbies": ["Skydiving", "Painting"],
            "income": 62000
        },
        {
            "id": "A103",
            "name": "Bob Harrison",
            "age": 35,
            "marital_status": "Married",
            "children": 3,
            "hobbies": ["Rock Climbing", "Running"],
            "income": 110000
        },
        {
            "id": "A104",
            "name": "Charlie Dunn",
            "age": 50,
            "marital_status": "Divorced",
            "children": 1,
            "hobbies": ["Photography", "Scuba Diving"],
            "income": 95000
        },
        {
            "id": "A105",
            "name": "Diana Prince",
            "age": 39,
            "marital_status": "Married",
            "children": 4,
            "hobbies": ["Hiking", "Tennis", "Baking"],
            "income": 105000
        },
        {
            "id": "A106",
            "name": "Edward Norton",
            "age": 61,
            "marital_status": "Widowed",
            "children": 0,
            "hobbies": ["Gardening", "Chess"],
            "income": 45000
        }
    ]
    
    # Write client data to individual JSON files
    for client in clients:
        file_path = os.path.join(apps_dir, f"client_{client['id']}.json")
        with open(file_path, 'w') as f:
            json.dump(client, f, indent=4)
            
    # Add some dirty data to test robustness
    with open(os.path.join(apps_dir, ".DS_Store"), 'w') as f:
        f.write("junk binary data")
        
    with open(os.path.join(apps_dir, "internal_memo.txt"), 'w') as f:
        f.write("CONFIDENTIAL: Do not process incomplete applications. - Management")

if __name__ == "__main__":
    build_env()
