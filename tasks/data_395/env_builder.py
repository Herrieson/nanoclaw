import os
import sqlite3
import random
import string

def build_env():
    base_dir = "assets/data_395"
    os.makedirs(base_dir, exist_ok=True)
    
    logs_dir = os.path.join(base_dir, "library_logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    # Create the SQLite DB
    db_path = os.path.join(base_dir, "library.db")
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE books (
            isbn TEXT PRIMARY KEY,
            title TEXT,
            author TEXT
        )
    """)
    conn.commit()
    conn.close()

    # Create notes.txt
    notes_content = """Oh dear, here are the ones I remember missing:
1. One was a classic science fiction book by 'Arthur C. Clarke'. The title had '2001' and 'Odyssey' in it.
2. Another one was that lovely little book about a prince. The author's name is French... 'Antoine de Saint-Exupery'.
3. My youngest son was looking for a book about space. I recall the author was 'Carl Sagan', and the title definitely had 'Cosmos' in it.
"""
    with open(os.path.join(base_dir, "notes.txt"), "w") as f:
        f.write(notes_content)
        
    # Generate random logs
    target_books = [
        ("978-0451457998", "2001: A Space Odyssey", "Arthur C. Clarke"),
        ("978-0156012195", "The Little Prince", "Antoine de Saint-Exupery"),
        ("978-0345331359", "Cosmos", "Carl Sagan")
    ]
    
    distractor_books = [
        ("978-0553293357", "Foundation", "Isaac Asimov"),
        ("978-0441272930", "Dune", "Frank Herbert"),
        ("978-0060850524", "Brave New World", "Aldous Huxley"),
        ("978-0451524935", "1984", "George Orwell"),
        ("978-0743273565", "The Great Gatsby", "F. Scott Fitzgerald")
    ]
    
    all_books = target_books + distractor_books
    
    for i in range(1, 6):
        log_file = os.path.join(logs_dir, f"syslog_backup_{i}.log")
        with open(log_file, "w") as f:
            for _ in range(100):
                # Write some garbage lines
                f.write(f"[{random.randint(1000, 9999)}] INFO: System process check {''.join(random.choices(string.ascii_letters, k=10))}\n")
                if random.random() < 0.1:
                    book = random.choice(all_books)
                    f.write(f"RECORD_FOUND >> ISBN: {book[0]} | Title: {book[1]} | Author: {book[2]}\n")

    # Ensure all target books are present at least once in the logs
    for i, book in enumerate(target_books):
        log_file = os.path.join(logs_dir, f"syslog_backup_{i+1}.log")
        with open(log_file, "a") as f:
            f.write(f"RECORD_FOUND >> ISBN: {book[0]} | Title: {book[1]} | Author: {book[2]}\n")

if __name__ == "__main__":
    build_env()
