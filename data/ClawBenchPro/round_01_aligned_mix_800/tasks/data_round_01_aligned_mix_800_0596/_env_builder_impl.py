import os
import json
import random
from datetime import datetime, timedelta

def build_env():
    random.seed(42) # Ensure determinism
    
    # Create main directories
    os.makedirs("messy_rsvps", exist_ok=True)
    os.makedirs("phone_backup", exist_ok=True)
    os.makedirs("store_policies", exist_ok=True)
    os.makedirs("party_plan", exist_ok=True)

    # 1. Distribute Policies (Noise + Clue)
    for i in range(1, 201):
        with open(f"store_policies/policy_doc_{i:03d}.json", "w") as f:
            if i == 147:
                # The Golden Clue
                data = {
                    "document_type": "event_catering_standards",
                    "version": "3.1",
                    "events": {
                        "annual_gala": {"burger": 0, "hotdog": 0, "beer": 0, "wine": 2},
                        "tailgate_bbq": {"burger": 2, "hotdog": 1, "beer": 4, "salad": 0},
                        "team_lunch": {"burger": 1, "hotdog": 0, "beer": 0, "soda": 2}
                    }
                }
            else:
                # Noise
                data = {
                    "document_type": random.choice(["dress_code", "attendance", "inventory_mgmt", "safety_protocol"]),
                    "policy_id": f"POL-{random.randint(1000, 9999)}",
                    "content": "Refer to main corporate guidelines."
                }
            json.dump(data, f, indent=2)

    # 2. Phone Backups (Noise + Clue)
    whitelist_real = ["Chad", "Big Mike", "Father Tom", "Gunner", "Dave from Receiving", "Gym Bro Steve", "Iron John"]
    whitelist_draft = ["Chad", "Big Mike", "Sneaky Pete"] # Decoy
    
    for i in range(1, 21):
        with open(f"phone_backup/chat_export_2023_vol_{i}.txt", "w") as f:
            f.write("--- CHAT LOG EXPORT ---\n")
            if i == 5:
                f.write("Brad: Here is the draft list...\n")
                f.write(f"Brad: {', '.join(whitelist_draft)}\n")
            elif i == 12:
                f.write("Brad: Alright boys, listen up! No more changes!\n")
                f.write("Brad: THIS IS THE FINAL BBQ WHITELIST!!! DO NOT SHARE THIS!\n")
                for name in whitelist_real:
                    f.write(f"- {name}\n")
                f.write("Brad: If you ain't on this list, you're eating gravel!\n")
            else:
                f.write(f"{random.choice(['Dave', 'Mike', 'Tom'])}: {random.choice(['lol', 'ok', 'gym time', 'see ya'])}\n")
                f.write("Brad: yeah bro\n")

    # 3. Messy RSVPs (Fragmentation + Multi-hop Logic + Scale)
    crashers = [f"Random Dude {i}" for i in range(1, 400)]
    all_people = whitelist_real + crashers
    
    base_time = int(datetime(2023, 10, 1).timestamp())
    
    rsvp_records = []
    
    # Generate random RSVPs for crashers
    for crasher in crashers:
        num_updates = random.randint(1, 2)
        for u in range(num_updates):
            rsvp_records.append({
                "guest_name": crasher,
                "extra_guests": random.randint(0, 5),
                "status": random.choice(["confirmed", "cancelled"]),
                "update_time": base_time + random.randint(1000, 500000)
            })

    # Generate specific RSVPs for Whitelist to test update logic and cancellation
    # Chad updates 3 times, final is confirmed with 2 extra
    rsvp_records.append({"guest_name": "Chad", "extra_guests": 1, "status": "confirmed", "update_time": base_time + 1000})
    rsvp_records.append({"guest_name": "Chad", "extra_guests": 0, "status": "confirmed", "update_time": base_time + 2000})
    rsvp_records.append({"guest_name": "Chad", "extra_guests": 2, "status": "confirmed", "update_time": base_time + 5000}) # Valid: 1+2=3

    # Big Mike submits once
    rsvp_records.append({"guest_name": "Big Mike", "extra_guests": 3, "status": "confirmed", "update_time": base_time + 1500}) # Valid: 1+3=4
    
    # Father Tom submits twice, finally cancels
    rsvp_records.append({"guest_name": "Father Tom", "extra_guests": 0, "status": "confirmed", "update_time": base_time + 100})
    rsvp_records.append({"guest_name": "Father Tom", "extra_guests": 0, "status": "cancelled", "update_time": base_time + 9000}) # Invalid (cancelled)
    
    # Gunner submits twice, changes extras
    rsvp_records.append({"guest_name": "Gunner", "extra_guests": 4, "status": "confirmed", "update_time": base_time + 800})
    rsvp_records.append({"guest_name": "Gunner", "extra_guests": 0, "status": "confirmed", "update_time": base_time + 3000}) # Valid: 1+0=1
    
    # Dave from Receiving
    rsvp_records.append({"guest_name": "Dave from Receiving", "extra_guests": 2, "status": "confirmed", "update_time": base_time + 4000}) # Valid: 1+2=3
    
    # Gym Bro Steve
    rsvp_records.append({"guest_name": "Gym Bro Steve", "extra_guests": 1, "status": "confirmed", "update_time": base_time + 2500}) # Valid: 1+1=2
    
    # Iron John cancels then confirms again
    rsvp_records.append({"guest_name": "Iron John", "extra_guests": 0, "status": "cancelled", "update_time": base_time + 1200})
    rsvp_records.append({"guest_name": "Iron John", "extra_guests": 1, "status": "confirmed", "update_time": base_time + 6000}) # Valid: 1+1=2

    # Shuffle all records to scatter them
    random.shuffle(rsvp_records)

    # Distribute them into nested subdirectories
    for i, record in enumerate(rsvp_records):
        # Create a deep messy folder structure based on hash-like dirs
        sub_dir = f"messy_rsvps/node_{i%10}/shard_{i%5}"
        os.makedirs(sub_dir, exist_ok=True)
        file_path = os.path.join(sub_dir, f"rsvp_entry_{i:04d}.json")
        with open(file_path, "w") as f:
            json.dump(record, f, indent=2)

if __name__ == "__main__":
    build_env()
