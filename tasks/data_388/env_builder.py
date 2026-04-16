import os
import base64

def build_env():
    # Define the base asset directory
    base_dir = "assets/data_388/mysterious_drive"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Create the cleaning log with a subtle hint
    log_content = """2023-10-01: Swept the main floor.
2023-10-02: Emptied trash near the DDR machine. Someone spilled soda again.
2023-10-03: Fixed the coin jam in Skee-Ball Lane 2.
2023-10-04: Note to self - The new VIP generator script is finished. 
            I encoded it in secret_data.b64 so the kids don't find it.
            Just decode it, run it with python, and pass the name as an argument.
2023-10-05: Cleaned the bathrooms.
"""
    with open(os.path.join(base_dir, "cleaning_log.txt"), "w") as f:
        f.write(log_content)

    # 2. Create the buggy python script
    script_content = """import sys
import os

if len(sys.argv) < 2:
    print("Error: You need to provide a name!")
    sys.exit(1)

# Get the name from the command line argument
name = sys.argv[1]

# BUG: Using undefined variable 'Name' instead of 'name'
pass_text = f"==================================\\n"
pass_text += f" ULTIMATE VIP ARCADE PASS FOR: {Name}\\n"
pass_text += f"==================================\\n"

# Write it out to the current working directory
with open('vip_pass.txt', 'w') as f:
    f.write(pass_text)

print("Pass generated successfully!")
"""
    
    # 3. Base64 encode the script and save it
    encoded_script = base64.b64encode(script_content.encode('utf-8')).decode('utf-8')
    with open(os.path.join(base_dir, "secret_data.b64"), "w") as f:
        f.write(encoded_script)

if __name__ == "__main__":
    build_env()
