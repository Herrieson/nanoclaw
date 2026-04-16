import os
import json
import random

def create_env():
    base_dir = "assets/data_37/raw_postcards"
    os.makedirs(base_dir, exist_ok=True)

    postcards = [
        # Valid ones
        {"id": "P001", "title": "Old Church in Dublin", "year": "1920", "tags": ["Ireland", "Architecture"], "sender_name": "Mary O'Brien", "sender_email": "mary@example.com"},
        {"id": "P002", "title": "St. Patrick's Cathedral", "year": "circa 1890", "tags": ["Catholic", "Historical"], "sender_name": "John Doe", "sender_email": "john@example.com"},
        {"id": "P003", "title": "Irish Countryside", "year": 1945, "tags": ["irish", "scenery"], "sender_name": "Sarah Connor", "sender_email": "sarah@example.com"},
        {"id": "P004", "title": "Holy Mass", "year": "1910", "tags": ["Religion", "Service"], "sender_name": "Father Ted", "sender_email": "ted@example.com"},
        
        # Invalid - Too new
        {"id": "P005", "title": "Modern Church in Galway", "year": "1960", "tags": ["Ireland", "Church"], "sender_name": "Alice Smith", "sender_email": "alice@example.com"},
        {"id": "P006", "title": "Pope John Paul II Visit", "year": "1979", "tags": ["Catholic", "Event"], "sender_name": "Bob Jones", "sender_email": "bob@example.com"},
        
        # Invalid - Has forbidden words
        {"id": "P007", "title": "Abstract Art of Irish Saints", "year": "1930", "tags": ["Ireland", "Abstract", "Religion"], "sender_name": "Hipster Dude", "sender_email": "art@example.com"},
        {"id": "P008", "title": "Contemporary Catholic Thoughts", "year": "1940", "tags": ["Catholic", "Literature"], "sender_name": "Writer Guy", "sender_email": "writer@example.com"},
        {"id": "P009", "title": "A modern look at religion", "year": "circa 1925", "tags": ["Religion"], "sender_name": "Reviewer", "sender_email": "rev@example.com"},
        
        # Invalid - No matching theme
        {"id": "P010", "title": "New York Skyline", "year": "1935", "tags": ["City", "USA"], "sender_name": "Uncle Sam", "sender_email": "sam@example.com"},
        {"id": "P011", "title": "Vintage Car", "year": 1922, "tags": ["Automobile"], "sender_name": "Mechanic", "sender_email": "mech@example.com"},
        
        # Valid - Messy formats
        {"id": "P012", "title": "Religious Procession", "year": "1938-05", "tags": ["religion"], "sender_name": "Sister Margaret", "sender_email": "margaret@example.com"},
        {"id": "P013", "title": "The Old Abbey", "year": " 1885 ", "tags": ["church", "ruins"], "sender_name": "Historian", "sender_email": "hist@example.com"}
    ]

    for i, pc in enumerate(postcards):
        # Mix file extensions to test robustness
        ext = ".json" if i % 2 == 0 else ".JSON"
        file_path = os.path.join(base_dir, f"record_{i:03d}{ext}")
        with open(file_path, 'w') as f:
            json.dump(pc, f, indent=2)
            
    # Add some noise files
    with open(os.path.join(base_dir, "notes.txt"), 'w') as f:
        f.write("Remember to sort out the modern stuff!\n")

if __name__ == "__main__":
    create_env()
