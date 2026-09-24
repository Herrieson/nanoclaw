import os
import json

def build_env():
    os.makedirs("messy_stuff", exist_ok=True)
    
    # Target 1: Valid json, target data
    with open("messy_stuff/asset_001.json", "w", encoding="utf-8") as f:
        json.dump({
            "author": "WiscArt99",
            "tier": "Epic",
            "item_name": "Frostbite Sword",
            "color": "#00FFFF",
            "sprite_data": "base64_dummy_data..."
        }, f)
        
    # Target 2: .tmp extension, target data
    with open("messy_stuff/asset_002.tmp", "w", encoding="utf-8") as f:
        json.dump({
            "author": "WiscArt99",
            "tier": "Legendary",
            "item_name": "Cheese Crown",
            "color": "#FFD700",
            "sprite_data": "base64_dummy_data..."
        }, f)
        
    # Target 3: .txt extension, target data
    with open("messy_stuff/asset_003.txt", "w", encoding="utf-8") as f:
        json.dump({
            "author": "WiscArt99",
            "tier": "Legendary",
            "item_name": "Cranberry Potion",
            "color": "#AA0033",
            "sprite_data": "base64_dummy_data..."
        }, f)
        
    # Junk 1: Wrong author
    with open("messy_stuff/asset_004.json", "w", encoding="utf-8") as f:
        json.dump({
            "author": "SomeGuy_88",
            "tier": "Legendary",
            "item_name": "Lame Axe",
            "color": "#FF0000",
            "sprite_data": "base64_dummy_data..."
        }, f)

    # Junk 2: Wrong tier (Common)
    with open("messy_stuff/asset_005.json", "w", encoding="utf-8") as f:
        json.dump({
            "author": "WiscArt99",
            "tier": "Common",
            "item_name": "Basic Boots",
            "color": "#888888",
            "sprite_data": "base64_dummy_data..."
        }, f)

    # Junk 3: Malformed JSON/dirty data
    with open("messy_stuff/asset_006.dat", "w", encoding="utf-8") as f:
        f.write("AUTHOR=WiscArt99\nTIER=Epic\nThis is a broken file that should fail standard json parsing {[[,,!")

if __name__ == "__main__":
    build_env()
