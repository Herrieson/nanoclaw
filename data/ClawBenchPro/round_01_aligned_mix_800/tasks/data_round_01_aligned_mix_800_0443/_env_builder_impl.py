import os
import csv
import json

def build_env():
    # 1. Generate fragmented raw_notes
    notes_dir = 'raw_notes'
    os.makedirs(notes_dir, exist_ok=True)
    
    # Generate 100 files across 5 nested directories to simulate scale and fragmentation
    for i in range(100):
        folder = os.path.join(notes_dir, f'batch_{i % 5}')
        os.makedirs(folder, exist_ok=True)
        filename = os.path.join(folder, f'v2t_{i:03d}.txt')
        
        lines = []
        # Create 3 lines per file using deterministic pseudo-randomness
        for j in range(3):
            month = ['09', '10', '11', '12'][(i + j) % 4]
            tag = ['#Toby', '#School', '#Hustle', '#Personal'][(i * j) % 4]
            day = (i + j) % 28 + 1
            event_date = f"2024-{month}-{day:02d}"
            
            if tag == '#Toby' and month == '11':
                desc = f"Pediatrician and daycare schedule id_{(i+j)}"
                line = f"[EventDate: {event_date}] {tag} {desc}"
            elif tag == '#Toby':
                line = f"[EventDate: {event_date}] {tag} Past/Future baby appt not for Nov"
            elif month == '11':
                line = f"[EventDate: {event_date}] {tag} Nov event but definitely not baby related"
            else:
                line = f"Just some random voice dump rambling about daily life {i}-{j}."
                
            lines.append(line)
            
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines) + "\n")
            
    # 2. Generate tech_hustle logs and separated receipts
    tech_dir = 'tech_hustle'
    receipts_dir = 'receipts'
    os.makedirs(tech_dir, exist_ok=True)
    os.makedirs(receipts_dir, exist_ok=True)
    
    csv_configs = [
        ('hustle_2024_01.csv', True),
        ('hustle_2024_02.csv', True),
        ('hustle_2024_03.csv', True),
        ('hustle_2024_04_backup.csv', False),
        ('hustle_2024_05_conflict_1.csv', False)
    ]
    
    job_id_counter = 1000
    for filename, is_valid in csv_configs:
        filepath = os.path.join(tech_dir, filename)
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Job_ID', 'Date', 'Device', 'Revenue', 'Status'])
            
            # 20 jobs per file
            for row_idx in range(20):
                job_id = f"JOB_{job_id_counter}"
                job_id_counter += 1
                
                # Deterministic status and logic
                status_cycle = ['Completed', 'Completed', 'Pending', 'Refunded']
                status = status_cycle[job_id_counter % 4]
                
                revenue = 100 + (job_id_counter % 50)
                writer.writerow([job_id, f"2024-10-01", "Device X", revenue, status])
                
                # Multi-hop Logic: Receipts generated separately in JSON format
                if status == 'Completed':
                    # 1 in 4 completed jobs will NOT have a receipt (Cost = 0)
                    if job_id_counter % 4 != 0:
                        cost = 20 + (job_id_counter % 10)
                        with open(os.path.join(receipts_dir, f"{job_id}.json"), 'w') as jf:
                            json.dump({"job_reference": job_id, "cost": cost, "vendor": "parts_r_us"}, jf)
                else:
                    # Decoys: Receipts for Pending/Refunded jobs to punish blind summing
                    if job_id_counter % 2 == 0:
                        cost = 30
                        with open(os.path.join(receipts_dir, f"{job_id}.json"), 'w') as jf:
                            json.dump({"job_reference": job_id, "cost": cost, "vendor": "fake_parts"}, jf)

if __name__ == '__main__':
    build_env()
