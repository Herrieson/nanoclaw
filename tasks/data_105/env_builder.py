import os
import base64
import json

def encrypt(text):
    key = b"HAHANOOB"
    res = bytearray()
    for i, b in enumerate(text.encode('utf-8')):
        res.append(b ^ key[i % len(key)])
    return base64.b64encode(res).decode('utf-8')

def build_env():
    base_dir = "assets/data_105"
    os.makedirs(base_dir, exist_ok=True)
    locked_dir = os.path.join(base_dir, "locked_comics")
    os.makedirs(locked_dir, exist_ok=True)

    # 1. Generate the encrypted comic summaries
    comics = {
        "issue_1_batman.txt": "Batman faces off against the Joker in the dark alleys of Gotham City. The stakes have never been higher, and Robin is missing.",
        "issue_2_superman.txt": "Superman returns to the ruins of Krypton to search for ancient artifacts, unaware that Lex Luthor has placed a tracker on his cape.",
        "issue_3_spiderman.txt": "Peter Parker struggles to balance his 7th-grade homework with swinging around Queens. The Green Goblin makes a surprise attack."
    }

    original_hashes = {}
    for filename, content in comics.items():
        enc_content = encrypt(content)
        enc_filename = filename + ".enc"
        with open(os.path.join(locked_dir, enc_filename), "w") as f:
            f.write(enc_content)
        # We don't save original files, we just let the agent figure it out.
        # But we save expected answers for verify_rules.py in a hidden place
    
    with open(os.path.join(base_dir, ".expected.json"), "w") as f:
        json.dump(comics, f)

    # 2. Generate the hacker's tool with missing decryption logic
    hacker_tool_code = """import base64
import sys
import os

# Hahaha! Your precious comics are mine!
SECRET_KEY = b"HAHANOOB"

def encrypt_file(filepath):
    with open(filepath, 'r') as f:
        text = f.read()
    
    res = bytearray()
    for i, b in enumerate(text.encode('utf-8')):
        res.append(b ^ SECRET_KEY[i % len(SECRET_KEY)])
    
    enc_data = base64.b64encode(res).decode('utf-8')
    
    enc_filepath = filepath + ".enc"
    with open(enc_filepath, 'w') as f:
        f.write(enc_data)
    
    os.remove(filepath)
    print(f"Encrypted {filepath}! Pay me in V-Bucks to get the decryption function!")

def decrypt_file(filepath):
    print("Nice try kid, the decryption function was deleted!")
    # TODO: write decryption logic here if they ever pay up

if __name__ == "__main__":
    print("Hacker Tool v1.0")
    # encrypt_file('some_comic.txt')
"""
    with open(os.path.join(base_dir, "hacker_tool.py"), "w") as f:
        f.write(hacker_tool_code)

    # 3. Generate notes from the kid
    notes = """I don't know what to do!!! 
All my files in 'locked_comics' end with .enc now.
I tried running hacker_tool.py but it just laughs at me. 
I need the files to be saved with their original names (without the .enc) in the 'locked_comics' folder.
I know the files used to be regular text files. I think it uses some kind of math on the letters? I failed my last math test so I have no idea.
Please help!!!
"""
    with open(os.path.join(base_dir, "notes.txt"), "w") as f:
        f.write(notes)

if __name__ == "__main__":
    build_env()
