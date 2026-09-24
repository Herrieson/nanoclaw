import os
import csv
import random
import datetime

def build_env():
    # Setup directories
    os.makedirs('server_logs', exist_ok=True)
    os.makedirs('artifact_submissions', exist_ok=True)
    
    regions = ['Asia', 'Europe', 'Americas', 'Africa', 'Oceania']
    for r in regions:
        os.makedirs(os.path.join('artifact_submissions', r), exist_ok=True)

    guests = [f"Guest_{i:03d}_{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))}" for i in range(1, 301)]
    
    # 1. Generate messy RSVP logs
    # We will spread them across multiple folders and files to simulate a broken server backup
    start_date = datetime.datetime(2023, 9, 1, 10, 0, 0)
    
    # Pre-calculate what the "final" state should be to ensure logic is solvable
    # But write them in random order across files
    log_entries = []
    
    for guest in guests:
        num_rsvps = random.randint(1, 4)
        current_time = start_date + datetime.timedelta(days=random.randint(0, 5), hours=random.randint(0, 23))
        
        for _ in range(num_rsvps):
            status = random.choice(['Confirmed', 'Declined', 'Pending'])
            extra = random.randint(0, 3)
            current_time += datetime.timedelta(days=random.randint(0, 2), hours=random.randint(1, 12))
            
            timestamp_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
            log_line = f"[{timestamp_str}] [RSVP-TICKET] GuestName: {guest} | Status: {status} | Extra: {extra}\n"
            log_entries.append(log_line)

    # Shuffle and write to fragmented log files with noise
    random.shuffle(log_entries)
    
    chunks = 15
    chunk_size = len(log_entries) // chunks + 1
    
    for i in range(chunks):
        dir_path = os.path.join('server_logs', f'backup_vol_{random.randint(10, 99)}')
        os.makedirs(dir_path, exist_ok=True)
        
        file_path = os.path.join(dir_path, f'syslog_{i}.txt')
        with open(file_path, 'w', encoding='utf-8') as f:
            for _ in range(random.randint(50, 100)): # Noise before
                f.write(f"[{start_date.strftime('%Y-%m-%d %H:%M:%S')}] [SYSTEM] Memory dump 0x{random.randint(1000,9999)} failed.\n")
            
            # Write real logs
            for entry in log_entries[i*chunk_size : (i+1)*chunk_size]:
                f.write(entry)
                # Interleaved noise
                if random.random() > 0.7:
                    f.write(f"[{start_date.strftime('%Y-%m-%d %H:%M:%S')}] [WARN] Timeout on socket {random.randint(10, 99)}\n")

    # 2. Generate Artifact submissions
    # Spread across regions
    for guest in guests:
        # Some guests don't submit artifacts at all
        if random.random() > 0.8:
            continue
            
        region = random.choice(regions)
        file_path = os.path.join('artifact_submissions', region, f'batch_{random.randint(1, 5)}.csv')
        
        artifact_status = random.choice(['Approved', 'Rejected', 'Pending'])
        # Bias towards Approved to have enough VIPs
        if random.random() > 0.5:
            artifact_status = 'Approved'
            
        artifact_name = f"Ancient {'Vase' if random.random()>0.5 else 'Sword'} of {random.randint(1,99)}"
        
        # Write to csv (append mode as multiple guests might hit the same file)
        file_exists = os.path.exists(file_path)
        with open(file_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['SubmissionID', 'GuestName', 'Item', 'Status', 'Inspector'])
            writer.writerow([f"SUB-{random.randint(1000,9999)}", guest, artifact_name, artifact_status, "Inspector_" + str(random.randint(1,5))])

if __name__ == "__main__":
    build_env()
