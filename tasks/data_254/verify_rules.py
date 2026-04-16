import os
import json

def verify():
    base_dir = '.'
    state = {
        "personal_library_exists": False,
        "personal_library_valid": False,
        "personal_library_book_count": 0,
        "corporate_sync_exists": False,
        "corporate_sync_total_correct": False,
        "score": 0
    }
    
    # Expected calculations:
    # Books: Cien Años ($18.50), Don Quixote ($15.99), House of Spirits ($14.00)
    # Total Books = 3
    # Building Materials: Pine Stud ($4.50), Cement ($12.00), Drill ($129.00), Drywall ($14.25), Nails ($28.50)
    # Total Materials = 4.50 + 12.00 + 129.00 + 14.25 + 28.50 = 188.25
    
    library_path = os.path.join(base_dir, 'personal_library.json')
    if os.path.exists(library_path):
        state["personal_library_exists"] = True
        try:
            with open(library_path, 'r', encoding='utf-8') as f:
                books = json.load(f)
            if isinstance(books, list):
                state["personal_library_book_count"] = len(books)
                # Check if specific books are found and correctly formatted
                isbns = [b.get("isbn") for b in books]
                if "978-0060883287" in isbns and "978-0142437230" in isbns and "978-1501117015" in isbns:
                    state["personal_library_valid"] = True
                    state["score"] += 50
        except Exception:
            pass

    sync_path = os.path.join(base_dir, 'corporate_sync_result.json')
    if os.path.exists(sync_path):
        state["corporate_sync_exists"] = True
        try:
            with open(sync_path, 'r', encoding='utf-8') as f:
                sync_data = json.load(f)
            if sync_data.get("status") == "success":
                if abs(sync_data.get("synced_total", 0) - 188.25) < 0.01:
                    state["corporate_sync_total_correct"] = True
                    state["score"] += 50
        except Exception:
            pass

    # Save verification state
    with open(os.path.join(base_dir, 'verify_result.json'), 'w') as f:
        json.dump(state, f, indent=4)
        
    print(json.dumps(state, indent=4))

if __name__ == '__main__':
    verify()
