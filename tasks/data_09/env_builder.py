import os
import json

def build_env():
    base_dir = "assets/data_09"
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Create color_notes directory and files
    notes_dir = os.path.join(base_dir, "color_notes")
    os.makedirs(notes_dir, exist_ok=True)
    
    # Note 1: Text format
    with open(os.path.join(notes_dir, "sunset.txt"), "w") as f:
        f.write("Sunset vibe:\nR: 255, G: 100, B: 50\nLove this for the top corner.")
        
    # Note 2: JSON format
    with open(os.path.join(notes_dir, "ocean.json"), "w") as f:
        json.dump({"theme": "ocean", "rgb": [10, 20, 30]}, f)
        
    # Note 3: CSV-like
    with open(os.path.join(notes_dir, "forest.csv"), "w") as f:
        f.write("name,r,g,b\nforest_deep,34,139,34\n")

    # 2. Create the buggy Python script
    buggy_script = """import json
import os

# Hey, I'm the script from the manufacturer!
def compile_frame():
    if not os.path.exists('palette.json'):
        print("Error: palette.json not found!")
        return

    with open('palette.json', 'r') as f:
        data = json.load(f)
        
    # Bug 1: hashlib is not imported
    # Bug 2: using list directly to string might have space variations, but let's just hash the strict json string
    json_str = json.dumps(data, separators=(',', ':'))
    m = hashlib.md5(json_str.encode('utf-8')).hexdigest()
    
    with open('canvas.bin', 'w') as f:
        f.write("SMARTCANVAS_" + m)

if __name__ == "__main__":
    compile_frame()
"""
    with open(os.path.join(base_dir, "compile_canvas.py"), "w") as f:
        f.write(buggy_script)

    # 3. Create the messy emails file
    emails_content = """
    Hey Sarah, don't forget soccer practice! mom@yahoo.com
    We need to email the curator at curator@gallery-az.com.
    Also, what about john.doe@scottsdale.art? He loved the last piece.
    spam account: free-money@scam.com
    My personal email is artist_mom_46@gmail.com
    Let's also reach out to the downtown gallery owner: boss@phoenix.art
    And maybe info@gallery-az.com for general inquiries.
    Fake email: fake@gallery-az.com.org (wait, this doesn't end in the right domain!)
    """
    with open(os.path.join(base_dir, "old_emails.txt"), "w") as f:
        f.write(emails_content)

if __name__ == "__main__":
    build_env()
