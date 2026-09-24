import os
import csv
import random

def build_env():
    # Set seed for deterministic but seemingly random wasteland generation
    random.seed(42)
    os.makedirs("scans", exist_ok=True)
    os.makedirs("archive_report", exist_ok=True)
    
    # 1. Create the messy QA Manifest with noise
    manifest_lines = [
        "=== ARCHIVE QA LOGS ===",
        "Note: Check batches carefully. Do not trust the temp folders.",
        "System Warning: Backup drive disconnected.",
        ""
    ]
    
    batches = []
    for i in range(1, 51):
        batch_name = f"batch_{i:03d}"
        status = random.choices(["Approved", "Rejected", "Pending"], weights=[0.4, 0.4, 0.2])[0]
        batches.append((batch_name, status))
        
        # Add noise to manifest
        date = f"2023-10-{random.randint(1, 28):02d}"
        inspector = random.choice(["Maria", "Carlos", "Temp_01"])
        manifest_lines.append(f"[{date}] Inspected {batch_name} by {inspector} - Status: {status}")
        manifest_lines.append(f"Comments: {random.choice(['Looks fine', 'A bit blurry', 'Needs review', 'Perfect', 'Missing pages, wait for rescan'])}")
        manifest_lines.append("")

    with open("scans/qa_manifest_v2_final.log", "w", encoding="utf-8") as f:
        f.write("\n".join(manifest_lines))
        
    call_num_counter = 1
    existing_call_nums = []
    
    # 2. Define the different header mutations
    header_formats = [
        ["Call_Number", "Title", "Author", "Scan_Date"],
        ["ID", "Book_Name", "Creator", "Date_Scanned"],
        ["ref_no", "name", "writer", "timestamp"]
    ]
    
    # 3. Generate massive fragmented files
    for batch_name, status in batches:
        batch_dir = f"scans/{batch_name}"
        os.makedirs(batch_dir, exist_ok=True)
        
        # Deeply nested machine folders
        for machine in ["station_alpha", "station_beta"]:
            machine_dir = f"{batch_dir}/{machine}"
            os.makedirs(machine_dir, exist_ok=True)
            
            num_files = random.randint(2, 5)
            for file_idx in range(num_files):
                # Inject noise extensions
                ext = random.choice([".csv", ".csv", ".bak", ".tmp"])
                filename = f"{machine_dir}/data_{file_idx}{ext}"
                
                header = random.choice(header_formats)
                rows = [header]
                
                num_rows = random.randint(10, 50)
                for _ in range(num_rows):
                    row_type = random.choices(
                        ["valid", "broken_no_id", "broken_no_title", "duplicate"], 
                        weights=[0.6, 0.15, 0.15, 0.1]
                    )[0]
                    
                    if row_type == "valid":
                        c_id = f"ESP-{call_num_counter:05d}"
                        title = f"Document history of {call_num_counter}"
                        rows.append([c_id, title, "AuthorX", "19XX"])
                        existing_call_nums.append(c_id)
                        call_num_counter += 1
                        
                    elif row_type == "broken_no_id":
                        title = f"Fragment {random.randint(1, 1000)}"
                        rows.append(["", title, "Unknown", "Unknown"])
                        
                    elif row_type == "broken_no_title":
                        c_id = f"ESP-{call_num_counter:05d}"
                        rows.append([c_id, "", "Unknown", "Unknown"])
                        call_num_counter += 1
                        
                    elif row_type == "duplicate" and existing_call_nums:
                        c_id = random.choice(existing_call_nums)
                        title = f"Document history of {c_id.split('-')[1]}"
                        rows.append([c_id, title, "Copied_Record", "19XX"])
                        
                with open(filename, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerows(rows)
                    
    # 4. Decoys and pure noise
    os.makedirs("scans/QA_Reject_Bin", exist_ok=True)
    with open("scans/QA_Reject_Bin/data_0.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Call_Number", "Title"])
        writer.writerow(["ESP-99999", "This should be ignored because the folder is not an approved batch"])

if __name__ == "__main__":
    build_env()
