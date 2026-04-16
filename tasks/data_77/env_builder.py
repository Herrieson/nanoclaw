import os
import random
from datetime import datetime, timedelta

def build_env():
    # Setup working directory
    base_dir = "assets/data_77"
    os.makedirs(base_dir, exist_ok=True)
    
    log_file_path = os.path.join(base_dir, "raw_observations.log")
    
    # Base configuration for data generation
    species_list = ['Piping Plover', 'Least Tern', 'Bald Eagle', 'Osprey', 'Blue Jay', 'American Robin']
    locations = ['Shelburne Bay', 'Lakefront Park', 'Downtown Marina', 'Winooski River', 'Mount Philo', 'Grand Isle']
    
    start_date = datetime(2023, 5, 1)
    
    logs = []
    
    # Generate noisy log lines
    for i in range(150):
        # Time progression
        record_time = start_date + timedelta(days=random.randint(0, 30), minutes=random.randint(0, 1440))
        time_str = record_time.strftime("%Y-%m-%d %H:%M:%S")
        
        species = random.choice(species_list)
        loc = random.choice(locations)
        lat = round(random.uniform(44.0, 45.0), 4)
        lng = round(random.uniform(-74.0, -72.0), 4)
        
        # Inject some garbage lines
        if random.random() < 0.1:
            logs.append(f"[{time_str}] ERROR: Component failure in sensor node 0x{random.randint(100,999)}\n")
            
        # The main observation format with mixed unstructured text and JSON
        user = f"student_{random.randint(1,50)}"
        
        # Add slight variations to species text to ensure matching isn't trivial but fair
        msg_species = species if random.random() < 0.8 else species.lower()
        
        log_line = f"[{time_str}] user: {user}, action: OBSERVATION, msg: I just spotted a {msg_species} near the water! {{\"lat\": {lat}, \"lng\": {lng}, \"loc\": \"{loc}\"}}"
        
        # Some malformed logs
        if random.random() < 0.05:
            log_line += " INCOMPLETE_DATA"
            
        logs.append(log_line + "\n")
        
    # Ensure there are specific target valid and invalid records
    manual_records = [
        '[2023-05-02 10:15:00] user: prof_k, action: OBSERVATION, msg: clear view of a Piping Plover here {"lat": 44.4759, "lng": -73.2121, "loc": "Shelburne Bay"}\n',
        '[2023-05-03 14:22:30] user: eco_stu, action: OBSERVATION, msg: Piping Plover spotted {"lat": 44.4800, "lng": -73.2200, "loc": "Lakefront Park"}\n', # Should be filtered
        '[2023-05-01 08:05:11] user: jane_d, action: OBSERVATION, msg: Least Tern feeding {"lat": 44.5012, "lng": -73.1905, "loc": "Grand Isle"}\n',
        '[2023-05-04 11:11:11] user: bob_b, action: OBSERVATION, msg: Least Tern resting {"lat": 44.4822, "lng": -73.2200, "loc": "Downtown Marina"}\n', # Should be filtered
        '[2023-05-05 09:30:00] user: alice_a, action: OBSERVATION, msg: saw Piping Plover {"lat": 44.4900, "lng": -73.2100, "loc": "Winooski River"}\n'
    ]
    
    logs.extend(manual_records)
    
    # Shuffle slightly, but keeping times mostly random
    random.shuffle(logs)
    
    with open(log_file_path, "w", encoding="utf-8") as f:
        f.writelines(logs)

if __name__ == "__main__":
    build_env()
