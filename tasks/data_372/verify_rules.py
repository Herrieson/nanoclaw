import os
import json
import csv

def verify():
    base_dir = "."
    fixed_csv_path = os.path.join(base_dir, "fixed_catalog.csv")
    quotes_json_path = os.path.join(base_dir, "recovered_quotes.json")
    
    state = {
        "fixed_csv_exists": False,
        "fixed_csv_valid": False,
        "recovered_quotes_exists": False,
        "recovered_quotes_valid": False,
        "errors": []
    }
    
    expected_books = {
        "1": {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "year": "1925"},
        "2": {"title": "1984", "author": "George Orwell", "year": "1949"},
        "3": {"title": "Pride and Prejudice", "author": "Jane Austen", "year": "1813"},
        "4": {"title": "To Kill a Mockingbird", "author": "Harper Lee", "year": "1960"},
        "5": {"title": "Frankenstein", "author": "Mary Shelley", "year": "1818"}
    }
    
    expected_quotes = {
        "The Great Gatsby": ["So we beat on, boats against the current, borne back ceaselessly into the past.", "I hope she'll be a fool."],
        "1984": ["Big Brother is watching you.", "War is peace. Freedom is slavery. Ignorance is strength."],
        "Pride and Prejudice": ["It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife."],
        "To Kill a Mockingbird": ["You never really understand a person until you consider things from his point of view."],
        "Frankenstein": ["Beware; for I am fearless, and therefore powerful."]
    }

    # Verify CSV
    if os.path.exists(fixed_csv_path):
        state["fixed_csv_exists"] = True
        try:
            with open(fixed_csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                valid = True
                row_count = 0
                for row in reader:
                    row_count += 1
                    b_id = row.get("ID")
                    if b_id in expected_books:
                        eb = expected_books[b_id]
                        if row.get("Title") != eb["title"] or row.get("Author") != eb["author"] or str(row.get("Year")) != eb["year"]:
                            valid = False
                            state["errors"].append(f"CSV mismatch for ID {b_id}: got {row}")
                    else:
                        valid = False
                
                if valid and row_count == 5:
                    state["fixed_csv_valid"] = True
                else:
                    state["errors"].append(f"CSV valid rows count mismatch. Found {row_count}, expected 5.")
        except Exception as e:
            state["errors"].append(f"Error reading fixed CSV: {str(e)}")
    else:
        state["errors"].append("fixed_catalog.csv not found.")

    # Verify JSON
    if os.path.exists(quotes_json_path):
        state["recovered_quotes_exists"] = True
        try:
            with open(quotes_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                valid = True
                for title, quotes in expected_quotes.items():
                    if title not in data:
                        valid = False
                        state["errors"].append(f"Missing title in JSON: {title}")
                        continue
                    
                    found_quotes = data[title]
                    if not isinstance(found_quotes, list) or set(found_quotes) != set(quotes):
                        valid = False
                        state["errors"].append(f"Quotes mismatch for '{title}'")
                
                if valid and len(data) == len(expected_quotes):
                    state["recovered_quotes_valid"] = True
        except Exception as e:
            state["errors"].append(f"Error reading JSON: {str(e)}")
    else:
        state["errors"].append("recovered_quotes.json not found.")

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
