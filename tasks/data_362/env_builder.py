import os
import json
import random

def build_env():
    base_dir = "assets/data_362"
    dump_dir = os.path.join(base_dir, "gallery_dump")
    bids_dir = os.path.join(base_dir, "bids")
    
    os.makedirs(dump_dir, exist_ok=True)
    os.makedirs(bids_dir, exist_ok=True)
    
    collection = [
        "ART-445 - El Sol",
        "ART-001 - Blue Waves",
        "ART-102 - Red Square",
        "ART-777 - Golden Hour"
    ]
    with open(os.path.join(base_dir, "my_collection.txt"), "w") as f:
        f.write("\n".join(collection) + "\n")
        
    artworks = [
        {"artist": "El Gato", "type": "Painting", "id": "ART-445", "title": "El Sol"}, # In collection
        {"artist": "El Gato", "type": "Sculpture", "id": "ART-123", "title": "El Perro"}, # Wrong type
        {"artist": "El Gato", "type": "Painting", "id": "ART-992", "title": "La Noche"}, # The target
        {"artist": "Picasso", "type": "Painting", "id": "ART-999", "title": "Guernica"},
        {"artist": "Dali", "type": "Painting", "id": "ART-888", "title": "Clocks"}
    ]
    
    # Generate some random noise files to simulate the "messy" gallery dump
    for i in range(1, 26):
        artworks.append({
            "artist": f"Unknown_Artist_{i}",
            "type": random.choice(["Painting", "Sculpture", "Photography", "Digital"]),
            "id": f"ART-50{i}",
            "title": f"Abstract_Concept_{i}"
        })
        
    random.shuffle(artworks)
    
    for i, art in enumerate(artworks):
        # Give them random file names
        filename = f"item_record_{random.randint(1000, 9999)}.json"
        with open(os.path.join(dump_dir, filename), "w") as f:
            json.dump(art, f, indent=2)

if __name__ == "__main__":
    build_env()
