import sys
import json

def get_conversion(term, ingredient):
    # Logic based on traditional kitchen lore
    conversions = {
        "handful": 0.5,
        "scoop": 1.0,
        "pinch": 0.1,
        "basket": 5.0
    }
    
    factor = conversions.get(term.lower(), 1.0)
    return json.dumps({
        "ingredient": ingredient,
        "original_term": term,
        "standard_unit_factor": factor,
        "note": f"In the heritage database, 1 {term} of {ingredient} is defined as {factor} units."
    })

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python heritage_recipe_decoder_skill.py <term> <ingredient>")
    else:
        print(get_conversion(sys.argv[1], sys.argv[2]))
