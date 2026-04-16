import os

def build_env():
    target_dir = "assets/data_451"
    os.makedirs(target_dir, exist_ok=True)
    
    cut_list_content = """Hey, here are the cuts for the new workbench:

Legs: 4 pieces at 34.5 in
Long stretchers: 4 pieces at 40 in
Short stretchers: 8 pieces at 21.25 in
Braces: 6 pieces at 15 in
Top supports: 2 pieces at 70 in

Material is 'Pine 2x4' for all of them. Make sure they are exact.
"""
    
    file_path = os.path.join(target_dir, "wood_cuts_list.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(cut_list_content)
        
    print(f"Environment built successfully at {target_dir}")

if __name__ == "__main__":
    build_env()
