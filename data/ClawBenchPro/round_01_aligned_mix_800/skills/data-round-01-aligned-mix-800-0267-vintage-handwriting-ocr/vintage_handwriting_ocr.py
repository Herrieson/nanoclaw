import os
import json

def parse_handwriting(file_path):
    if not os.path.exists(file_path):
        return json.dumps({"error": f"File not found: {file_path}"})
    
    # We simulate a perfect OCR reading of the vintage Abuela recipe
    simulated_extraction = {
        "document_type": "handwritten_recipe",
        "title": "Abuela's Birria",
        "servings": 5,
        "ingredients": {
            "beef_chuck_lbs": 3,
            "dried_guajillo_chiles": 6,
            "garlic_cloves": 4,
            "onion": 1,
            "corn_tortillas_pack": 1
        },
        "notes": "Cook with love!"
    }
    
    return json.dumps(simulated_extraction, indent=2)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(parse_handwriting(sys.argv[1]))
    else:
        print('Error: Missing file_path parameter.')
