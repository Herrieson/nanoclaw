import os
import csv
import sqlite3

def build_env():
    base_dir = "assets/data_320"
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Create the messy CSV file
    csv_path = os.path.join(base_dir, "reading_logs_corrupted.csv")
    csv_data = [
        ["Student_Name", "School_ID", "Book_Title", "Minutes_Read"],
        ["Alice", "S01", " Moby dick", "120"],
        ["Bob", "S01", "The Great Gatsby ", "45"],
        ["Charlie", "S02", "Twilight", "200"],
        ["Alice", "S01", "1984 ", "30"],
        ["Diana", "S02", " 1984", "90"],
        ["Eve", "S01", "moby Dick", "60"],
        ["Frank", "S03", "The Hunger Games", "150"],
        ["Bob", "S01", " the odyssey", "15"],
        ["Grace", "S03", "PRIDE AND PREJUDICE", "180"],
        ["Henry", "S02", "harry potter", "300"]
    ]
    
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        # Deliberately using pipe delimiter to add a tiny bit of parsing friction
        writer = csv.writer(f, delimiter="|")
        writer.writerows(csv_data)
        
    # 2. Create the SQLite database
    db_path = os.path.join(base_dir, "blog_books.db")
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            is_classic INTEGER NOT NULL,
            rating INTEGER
        )
    ''')
    
    # Clean titles in the DB to test agent's ability to normalize the CSV
    db_books = [
        ("Moby Dick", "Herman Melville", 1, 5),
        ("The Great Gatsby", "F. Scott Fitzgerald", 1, 4),
        ("Twilight", "Stephenie Meyer", 0, 1),
        ("1984", "George Orwell", 1, 5),
        ("The Hunger Games", "Suzanne Collins", 0, 2),
        ("The Odyssey", "Homer", 1, 5),
        ("Pride and Prejudice", "Jane Austen", 1, 5),
        ("Harry Potter", "J.K. Rowling", 0, 3)
    ]
    
    cursor.executemany("INSERT INTO reviews (title, author, is_classic, rating) VALUES (?, ?, ?, ?)", db_books)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    build_env()
