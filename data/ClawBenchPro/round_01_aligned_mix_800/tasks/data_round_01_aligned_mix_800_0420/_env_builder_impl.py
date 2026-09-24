import os
import json
import csv
import random
import uuid

def build_env():
    # Setup directories
    base_recovery = 'RECOVERY_DUMP_0524'
    base_clients = 'CLIENT_DATA_ARCHIVE'
    os.makedirs(base_recovery, exist_ok=True)
    os.makedirs(base_clients, exist_ok=True)

    names = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Heidi"]
    diets = ["Vegan", "Gluten-Free", "Nut Allergy", "Paleo", "Keto", "None"]
    
    # 1. Create fragmented Client Profiles
    # We'll split the profiles into 50 tiny JSON shards, most of which are decoys
    for i in range(50):
        shard_name = f"shard_{uuid.uuid4().hex[:8]}.json"
        is_real = i < len(names)
        if is_real:
            data = {
                "id": i,
                "name": names[i],
                "meta": {
                    "diet": random.choice(diets),
                    "rsvp": random.choice([True, False])
                }
            }
        else:
            data = {"id": i, "garbage": "data_segment_" + str(random.random())}
        
        # Deeply nest some of them
        depth_dir = os.path.join(base_clients, f"subdir_{i%5}")
        os.makedirs(depth_dir, exist_ok=True)
        with open(os.path.join(depth_dir, shard_name), 'w') as f:
            json.dump(data, f)

    # 2. Create "Wasteland" Log Files
    # Formula: (HR - 60) * Mins * 0.15
    # Valid logs: must have 'checksum' and status='completed'
    
    # Generate 200 files, only 10-15 are "real"
    for i in range(200):
        folder = os.path.join(base_recovery, f"node_{i//20}")
        os.makedirs(folder, exist_ok=True)
        
        file_ext = random.choice(['csv', 'txt', 'tmp', 'log'])
        filename = f"recov_{i:03d}.{file_ext}"
        filepath = os.path.join(folder, filename)
        
        is_valid = i % 15 == 0
        
        if is_valid and file_ext == 'csv':
            # Real CSV log
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['user', 'duration', 'hr_avg', 'status', 'checksum'])
                # Alice: (140-60)*45*0.15 = 540
                writer.writerow(['Alice', '45', '140', 'completed', 'CRC32_X66'])
                # Bob: (120-60)*30*0.15 = 270
                writer.writerow(['Bob', '30', '120', 'completed', 'CRC32_Y12'])
                # Distractor in valid file
                writer.writerow(['Charlie', '60', '180', 'cancelled', 'CRC32_Z99'])
        
        elif is_valid and file_ext == 'txt':
            # Real TXT log with semi-structured data
            content = "SESSION_START\n"
            # David: (150-60)*40*0.15 = 540
            content += "USER:David|DUR:40|HR:150|STAT:completed|CHK:CRC32_A1\n"
            # Alice: (100-60)*60*0.15 = 360 (Total Alice = 540+360=900)
            content += "USER:Alice|DUR:60|HR:100|STAT:completed|CHK:CRC32_B2\n"
            content += "SESSION_END"
            with open(filepath, 'w') as f:
                f.write(content)
        
        elif is_valid: # Other extensions but valid content
            # JSON format
            data = [
                {"user": "Charlie", "duration": 50, "hr_avg": 160, "status": "completed", "checksum": "CRC32_C3"}, # 750
                {"user": "Eve", "duration": 20, "hr_avg": 120, "status": "completed", "checksum": "CRC32_D4"}     # 180
            ]
            with open(filepath, 'w') as f:
                json.dump(data, f)
        
        else:
            # Noise/Junk files
            with open(filepath, 'w') as f:
                if file_ext == 'csv':
                    f.write("wrong,header,no,checksum\nnoise,0,0,noise")
                else:
                    f.write(f"Corrupted segment {uuid.uuid4().hex} ... system error 0x404")

if __name__ == '__main__':
    build_env()
