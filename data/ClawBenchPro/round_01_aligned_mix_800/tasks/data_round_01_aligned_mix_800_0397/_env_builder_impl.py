import os

def build_env():
    os.makedirs("messy_stuff", exist_ok=True)
    
    # Custom packed format: MOD_ASSET_V2.4\nAUTHOR:[name]\nASSET_REF:[id]
    
    # Target 1: Valid json, target data
    with open("messy_stuff/asset_001.json", "w", encoding="utf-8") as f:
        f.write("MOD_ASSET_V2.4\nAUTHOR:WiscArt99\nASSET_REF:001_FROSTBITE\nBLOB:e3VyaX0=")
        
    # Target 2: .tmp extension, target data
    with open("messy_stuff/asset_002.tmp", "w", encoding="utf-8") as f:
        f.write("MOD_ASSET_V2.4\nAUTHOR:WiscArt99\nASSET_REF:002_CHEESE\nBLOB:q1p5b30=")
        
    # Target 3: .txt extension, target data
    with open("messy_stuff/asset_003.txt", "w", encoding="utf-8") as f:
        f.write("MOD_ASSET_V2.4\nAUTHOR:WiscArt99\nASSET_REF:003_CRANBERRY\nBLOB:m9k2a11=")
        
    # Junk 1: Wrong author
    with open("messy_stuff/asset_004.json", "w", encoding="utf-8") as f:
        f.write("MOD_ASSET_V2.4\nAUTHOR:SomeGuy_88\nASSET_REF:004_LAME\nBLOB:h4g7l90=")

    # Junk 2: Wrong tier (Common) -> Hidden in ASSET_REF logic, but author matches
    with open("messy_stuff/asset_005.json", "w", encoding="utf-8") as f:
        f.write("MOD_ASSET_V2.4\nAUTHOR:WiscArt99\nASSET_REF:005_BASIC\nBLOB:v0c2z33=")

    # Junk 3: Malformed data
    with open("messy_stuff/asset_006.dat", "w", encoding="utf-8") as f:
        f.write("AUTHOR=WiscArt99\nTIER=Epic\nThis is a broken file that should fail any unpacking tool {[[,,!")

if __name__ == "__main__":
    build_env()
