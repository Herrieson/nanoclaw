import os
import sqlite3
import json
import yaml
import random

def build_env():
    base_dir = "assets/data_211"
    os.makedirs(base_dir, exist_ok=True)
    schedules_dir = os.path.join(base_dir, "feed_schedules")
    os.makedirs(schedules_dir, exist_ok=True)

    # 1. Create SQLite Database for Animal Registry
    db_path = os.path.join(base_dir, "animal_registry.sqlite")
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE animals (
            id TEXT PRIMARY KEY,
            name TEXT,
            species TEXT,
            age INTEGER
        )
    ''')

    # Insert some dummy animals and our target animals
    animals_data = [
        ("A-001", "Max", "Dog", 5),
        ("A-002", "Bella", "Cat", 3),
        ("A-003", "Kotaro", "Shiba Inu", 2),
        ("A-004", "Charlie", "Parrot", 10),
        ("A-005", "Shirayuki", "Red-crowned Crane", 4),
        ("A-006", "Luna", "Rabbit", 1)
    ]
    cursor.executemany("INSERT INTO animals (id, name, species, age) VALUES (?, ?, ?, ?)", animals_data)
    conn.commit()
    conn.close()

    # 2. Create YAML feed schedules
    for a_id, name, _, _ in animals_data:
        schedule = {
            "animal_id": a_id,
            "meals_per_day": random.choice([1, 2, 3]),
            "food_type": "generic_kibble" if name != "Shirayuki" else "seeds",
            "protein_level": "low" if name == "Kotaro" else "normal",
            "supplements": []
        }
        with open(os.path.join(schedules_dir, f"{a_id}_schedule.yaml"), 'w') as f:
            yaml.dump(schedule, f)

    # 3. Create Exhibits JSON
    exhibits_data = {
        "museum_wings": [
            {
                "wing_name": "Ancient Japan",
                "artifacts": [
                    {
                        "artifact_id": "EX-101",
                        "name": "Samurai Armor",
                        "period": "Edo Period",
                        "material": "Metal, Leather",
                        "humidity": 50,
                        "temperature": 20
                    },
                    {
                        "artifact_id": "EX-102",
                        "name": "Painted Folding Screen",
                        "period": "Edo Period",
                        "material": "Wood, Paper",
                        "humidity": 80, 
                        "temperature": 21
                    },
                    {
                        "artifact_id": "EX-103",
                        "name": "Jomon Pottery",
                        "period": "Jomon Period",
                        "material": "Clay",
                        "humidity": 60,
                        "temperature": 22
                    },
                    {
                        "artifact_id": "EX-104",
                        "name": "Ukiyo-e Woodblock Print",
                        "period": "Edo Period",
                        "material": "Paper",
                        "humidity": 75,
                        "temperature": 19
                    },
                    {
                        "artifact_id": "EX-105",
                        "name": "Katana Sword",
                        "period": "Muromachi Period",
                        "material": "Steel",
                        "humidity": 40,
                        "temperature": 20
                    }
                ]
            }
        ]
    }
    
    with open(os.path.join(base_dir, "exhibits_config.json"), 'w') as f:
        json.dump(exhibits_data, f, indent=4)

if __name__ == "__main__":
    build_env()
