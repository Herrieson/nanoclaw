import os
import random
import string

def setup_env():
    base_dir = "assets/data_376"
    os.makedirs(base_dir, exist_ok=True)
    
    jobs_dir = os.path.join(base_dir, "print_jobs")
    
    # Create a messy directory structure
    dirs = [
        "2023_archive/q1",
        "2023_archive/q2/corrupted",
        "recent/monday",
        "recent/tuesday/morning_run",
        "misc/unknown",
        "new_folder/new_folder_2"
    ]
    
    for d in dirs:
        os.makedirs(os.path.join(jobs_dir, d), exist_ok=True)

    # Golden records (Must be found)
    golden_data = [
        ("[JOB:9921] [CUST:Acme Corp] [INK:CMYK] [QTY:8500] [STATUS:PENDING]", "recent/monday/job_9921.spl"),
        ("[JOB:8834] [CUST:TechPrint] [INK:CMYK] [QTY:12000] [STATUS:QUEUED]", "2023_archive/q2/corrupted/rec_8834.log"),
        ("Some junk data before... [JOB:7712] [CUST:Global Flyers] [INK:CMYK] [QTY:5001] [STATUS:PENDING] ...and some junk after.", "misc/unknown/flyers.spl")
    ]
    
    # Decoy records (Must NOT be found/included)
    decoy_data = [
        ("[JOB:1122] [CUST:Local Bakery] [INK:BW] [QTY:10000] [STATUS:PENDING]", "recent/tuesday/morning_run/job_1122.spl"), # Wrong INK
        ("[JOB:3344] [CUST:School District] [INK:CMYK] [QTY:5000] [STATUS:PENDING]", "new_folder/new_folder_2/school.log"), # QTY not > 5000
        ("[JOB:5566] [CUST:City Hall] [INK:CMYK] [QTY:4500] [STATUS:DONE]", "recent/monday/job_5566.spl"), # QTY too low
        ("[JOB:7788] [CUST:Fake Biz] [INK:SPOT] [QTY:20000] [STATUS:QUEUED]", "2023_archive/q1/spot_job.spl") # Wrong INK
    ]

    all_data = golden_data + decoy_data

    # Write the files
    for content, path_suffix in all_data:
        full_path = os.path.join(jobs_dir, path_suffix)
        with open(full_path, "w", encoding="utf-8") as f:
            # Add some random garbage lines to simulate raw spool logs
            f.write(f"HDR_START {random.randint(1000,9999)}\n")
            f.write("".join(random.choices(string.ascii_letters, k=20)) + "\n")
            f.write(content + "\n")
            f.write("EOF\n")

    # Add some pure garbage files
    for i in range(5):
        garbage_path = os.path.join(jobs_dir, dirs[i], f"temp_{i}.tmp")
        with open(garbage_path, "wb") as f:
            f.write(os.urandom(128))

    # Write the broken script
    broken_script = """import os
import re

# i don't know why this isn't working, the kid was crying
# just need CMYK and qty > 5000
def get_jobs():
    for root, dirs, files in os.walk('print_jobs'):
        for f in files:
            # wait, how do I open the file?
            with open(f, 'r') as file: 
                data = file.read()
                if "CMYK" in data:
                    print(data) # need to put this in csv later

get_jobs()
"""
    with open(os.path.join(base_dir, "extract.py"), "w", encoding="utf-8") as f:
        f.write(broken_script)

if __name__ == "__main__":
    setup_env()
