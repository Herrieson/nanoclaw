import os
import csv
import random

def build_env():
    base_dir = "assets/data_372"
    dumps_dir = os.path.join(base_dir, "dumps")
    
    os.makedirs(dumps_dir, exist_ok=True)
    
    books = [
        {"id": 1, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "year": 1925, "genre": "Fiction", "quotes": ["So we beat on, boats against the current, borne back ceaselessly into the past.", "I hope she'll be a fool."]},
        {"id": 2, "title": "1984", "author": "George Orwell", "year": 1949, "genre": "Dystopian", "quotes": ["Big Brother is watching you.", "War is peace. Freedom is slavery. Ignorance is strength."]},
        {"id": 3, "title": "Pride and Prejudice", "author": "Jane Austen", "year": 1813, "genre": "Romance", "quotes": ["It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife."]},
        {"id": 4, "title": "To Kill a Mockingbird", "author": "Harper Lee", "year": 1960, "genre": "Fiction", "quotes": ["You never really understand a person until you consider things from his point of view."]},
        {"id": 5, "title": "Frankenstein", "author": "Mary Shelley", "year": 1818, "genre": "Horror", "quotes": ["Beware; for I am fearless, and therefore powerful."]}
    ]
    
    # Generate scrambled CSV
    csv_path = os.path.join(base_dir, "scrambled_catalog.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Title", "Author", "Year", "Genre"]) # Header remains, but data is swapped
        for b in books:
            # Swap title and author, hex encode year
            writer.writerow([b["id"], b["author"], b["title"], hex(b["year"]), b["genre"]])
            
            # Generate dump file
            dump_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 10
            for q in b["quotes"]:
                # Insert quotes with brackets at random places
                parts = dump_text.split()
                insert_idx = random.randint(0, len(parts))
                parts.insert(insert_idx, f"[[{q}]]")
                dump_text = " ".join(parts)
            
            dump_file = os.path.join(dumps_dir, f"dump_{b['id']}.txt")
            with open(dump_file, 'w', encoding='utf-8') as df:
                df.write(dump_text)

if __name__ == "__main__":
    build_env()
