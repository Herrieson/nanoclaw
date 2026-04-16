import os
import json

def verify():
    result = {
        "cookbook_exists": False,
        "grandmas_decoded_correctly": False,
        "green_bean_included": False,
        "irish_bread_included": False
    }

    # Agent might create it in current dir or the assets dir
    possible_paths = [
        "final_cookbook.md",
        "final_cookbook.md",
        "final_cookbook.md"
    ]
    
    cookbook_path = None
    for p in possible_paths:
        if os.path.exists(p):
            cookbook_path = p
            break

    if cookbook_path:
        result["cookbook_exists"] = True
        with open(cookbook_path, 'r', encoding='utf-8') as f:
            content = f.read()

            # Check for decoded content
            if "Grandma's Secret Peach Cobbler" in content and "A pinch of salt and a lot of love!" in content:
                result["grandmas_decoded_correctly"] = True
            
            # Check for other recipes
            if "Green Bean Casserole" in content and "mushroom soup" in content:
                result["green_bean_included"] = True
                
            if "Traditional Irish Soda Bread" in content and "buttermilk" in content:
                result["irish_bread_included"] = True

    # Write out the state
    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
