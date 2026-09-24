import os
import json
import random
import string

def get_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_garbage_binary(size):
    return bytes((random.getrandbits(8) for _ in range(size)))

def build_env():
    random.seed(1335)
    base_dir = "messy_stuff"
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Create a deep labyrinth of directories
    dirs = [base_dir]
    for depth in range(3):
        new_dirs = []
        for parent in dirs:
            for _ in range(3): # branching factor
                folder_name = get_random_string(4)
                path = os.path.join(parent, folder_name)
                os.makedirs(path, exist_ok=True)
                new_dirs.append(path)
        dirs.extend(new_dirs)
        
    extensions = ['.tmp', '.txt', '.dat', '.json', '.bak', '.log', '.swp', '', '.csv', '.bin']
    
    # 2. Generate Decoys and Junk
    
    # Type A: Pure binary junk (Invalid UTF-8)
    for i in range(150):
        target_dir = random.choice(dirs)
        fname = f"junk_bin_{get_random_string(6)}{random.choice(extensions)}"
        with open(os.path.join(target_dir, fname), "wb") as f:
            f.write(generate_garbage_binary(random.randint(500, 2000)))

    # Type B: Broken strings/logs that contain keywords to fool grep/regex
    for i in range(200):
        target_dir = random.choice(dirs)
        fname = f"log_{get_random_string(6)}{random.choice(extensions)}"
        with open(os.path.join(target_dir, fname), "w", encoding="utf-8") as f:
            f.write(f"ERROR: Failed to load asset.\nauthor: WiscArt99\ntier: Legendary\nitem_name: FakeItem_{i}\nThis is not a JSON {{[}}!")

    # Type C: Valid JSON, but wrong Author
    for i in range(150):
        target_dir = random.choice(dirs)
        fname = f"asset_{get_random_string(6)}{random.choice(extensions)}"
        author = random.choice(["WiscArt_99", "WiscArt99 ", "SomeGuy88", "WiscArt", "WISCART99"])
        with open(os.path.join(target_dir, fname), "w", encoding="utf-8") as f:
            json.dump({
                "author": author,
                "tier": "Epic",
                "item_name": f"Decoy Blade {i}",
                "color": "#FF0000",
                "sprite_data": get_random_string(100)
            }, f)

    # Type D: Valid JSON, correct Author, wrong Tier
    for i in range(150):
        target_dir = random.choice(dirs)
        fname = f"asset_{get_random_string(6)}{random.choice(extensions)}"
        with open(os.path.join(target_dir, fname), "w", encoding="utf-8") as f:
            json.dump({
                "author": "WiscArt99",
                "tier": random.choice(["Common", "Rare", "Mythic", "Junk"]),
                "item_name": f"Basic Shield {i}",
                "color": "#888888",
                "sprite_data": get_random_string(100)
            }, f)

    # Type E: Valid JSON, correct Author/Tier, missing item_name or color (Tests robustness of dict.get())
    for i in range(80):
        target_dir = random.choice(dirs)
        fname = f"broken_asset_{get_random_string(6)}{random.choice(extensions)}"
        data = {
            "author": "WiscArt99",
            "tier": random.choice(["Epic", "Legendary"]),
            "sprite_data": get_random_string(100)
        }
        if random.random() > 0.5:
            data["item_name"] = f"Missing Color Wand {i}"
        else:
            data["color"] = "#123456"
            
        with open(os.path.join(target_dir, fname), "w", encoding="utf-8") as f:
            json.dump(data, f)

    # 3. Generate Targets (The Holy Grails)
    adjectives = ["Frostbite", "Infernal", "Celestial", "Shadow", "Luminous", "Void", "Crimson"]
    nouns = ["Sword", "Axe", "Staff", "Crown", "Boots", "Amulet", "Gauntlet"]
    
    target_count = 42
    for i in range(target_count):
        target_dir = random.choice(dirs)
        fname = f"real_asset_{get_random_string(6)}{random.choice(extensions)}"
        item_name = f"{random.choice(adjectives)} {random.choice(nouns)} {i}"
        color = f"#{random.randint(0, 0xFFFFFF):06X}"
        
        with open(os.path.join(target_dir, fname), "w", encoding="utf-8") as f:
            json.dump({
                "author": "WiscArt99",
                "tier": random.choice(["Epic", "Legendary"]),
                "item_name": item_name,
                "color": color,
                "sprite_data": get_random_string(150),
                "timestamp": 1690000000 + i
            }, f)

if __name__ == "__main__":
    build_env()
