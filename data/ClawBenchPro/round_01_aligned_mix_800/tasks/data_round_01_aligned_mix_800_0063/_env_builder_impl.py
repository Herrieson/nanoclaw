import os
import argparse
import json
import shutil

def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def build_turn_1():
    os.makedirs("submissions", exist_ok=True)
    os.makedirs("results", exist_ok=True)
    
    artworks = [
        # Valid, cheap, but is a sculpture (will be banned in turn 2)
        {"id": "art_01", "artist_name": "John Smith", "state": "AR", "medium": "Sculpture", "price": 150, "weight_lbs": 30, "tags": ["peace"]},
        # Valid, very cheap, will be selected
        {"id": "art_02", "artist_name": "Jane Doe", "state": "AR", "medium": "Watercolor", "price": 200, "weight_lbs": 2, "tags": ["nature"]},
        # Invalid state
        {"id": "art_03", "artist_name": "Bob Ross", "state": "TX", "medium": "Oil Painting", "price": 100, "weight_lbs": 5, "tags": ["quiet"]},
        # Invalid medium
        {"id": "art_04", "artist_name": "Alice Wonderland", "state": "AR", "medium": "Digital Art", "price": 50, "weight_lbs": 1, "tags": ["home"]},
        # Valid, cheap, will be selected
        {"id": "art_05", "artist_name": "Charlie Smith", "state": "AR", "medium": "Acrylic", "price": 300, "weight_lbs": 8, "tags": ["home", "quiet"]},
        # Valid, expensive
        {"id": "art_06", "artist_name": "Diana Prince", "state": "AR", "medium": "Oil Painting", "price": 1200, "weight_lbs": 15, "tags": ["peace"]},
        # Valid, cheap sculpture (will be banned in turn 2 due to weight > 20)
        {"id": "art_07", "artist_name": "Evan Miller", "state": "AR", "medium": "Sculpture", "price": 250, "weight_lbs": 25, "tags": ["nature"]},
        # Valid, moderate price
        {"id": "art_08", "artist_name": "Fiona Apple", "state": "AR", "medium": "Oil Painting", "price": 400, "weight_lbs": 10, "tags": ["quiet"]},
        # Valid, cheap, but heavy painting (will be banned in turn 2)
        {"id": "art_09", "artist_name": "George Miller", "state": "AR", "medium": "Acrylic", "price": 350, "weight_lbs": 22, "tags": ["home"]},
        # Valid, moderate
        {"id": "art_10", "artist_name": "Hannah Abbott", "state": "AR", "medium": "Watercolor", "price": 300, "weight_lbs": 4, "tags": ["peace"]},
        # Valid, cheap sculpture, weight < 20 (but still banned in turn 2 because it's a sculpture)
        {"id": "art_11", "artist_name": "Ian McKellen", "state": "AR", "medium": "Sculpture", "price": 100, "weight_lbs": 10, "tags": ["home"]}
    ]
    
    # In Turn 1: 
    # Budget 2000. Goal: max pieces.
    # Valid pool:
    # art_11: 100
    # art_01: 150
    # art_02: 200
    # art_07: 250
    # art_05: 300
    # art_10: 300
    # art_09: 350
    # art_08: 400
    # Total for these 8 = 2050. We can pick 7 pieces to maximize count.
    # We drop the most expensive (art_08, 400). Total spent = 1650.
    
    for art in artworks:
        write_json(f"submissions/{art['id']}.json", art)

def build_turn_2():
    # Assume previous state is kept by the framework.
    os.makedirs("new_submissions", exist_ok=True)
    
    new_artworks = [
        # Valid spiritual replacement, cheap
        {"id": "art_12", "artist_name": "Kevin Doe", "state": "AR", "medium": "Watercolor", "price": 200, "weight_lbs": 3, "tags": ["spiritual", "quiet"]},
        # Valid spiritual replacement, moderate
        {"id": "art_13", "artist_name": "Laura Smith", "state": "AR", "medium": "Oil Painting", "price": 400, "weight_lbs": 12, "tags": ["faith", "peace"]},
        # Invalid: spiritual but it's a sculpture
        {"id": "art_14", "artist_name": "Mike Johnson", "state": "AR", "medium": "Sculpture", "price": 150, "weight_lbs": 5, "tags": ["spiritual", "home"]},
        # Invalid: spiritual but heavy
        {"id": "art_15", "artist_name": "Nancy Drew", "state": "AR", "medium": "Acrylic", "price": 300, "weight_lbs": 25, "tags": ["faith", "nature"]},
        # Valid, but too expensive to include while maximizing count
        {"id": "art_16", "artist_name": "Oscar Wilde", "state": "AR", "medium": "Watercolor", "price": 1500, "weight_lbs": 5, "tags": ["spiritual", "peace"]}
    ]
    
    for art in new_artworks:
        write_json(f"new_submissions/{art['id']}.json", art)

def build_turn_3():
    # The final list going into turn 3 should be:
    # Non-banned from turn 1: art_02(200), art_05(300), art_10(300), art_08(400) -> total 1200
    # Spiritual additions from turn 2: art_12(200), art_13(400) -> total 600
    # Grand total: 1800. 6 pieces total.
    # Note names:
    # art_02: Jane Doe
    # art_05: Charlie Smith
    # art_10: Hannah Abbott
    # art_08: Fiona Apple
    # art_12: Kevin Doe
    # art_13: Laura Smith
    # Doe family: art_02, art_12
    # Smith family: art_05, art_13
    
    venue_layout = {
        "Wall_North": {"max_pieces": 3, "max_weight_lbs": 20},
        "Wall_East": {"max_pieces": 2, "max_weight_lbs": 15},
        "Wall_West": {"max_pieces": 2, "max_weight_lbs": 25}
    }
    
    write_json("venue_layout.json", venue_layout)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
    elif args.turn == 3:
        build_turn_3()
