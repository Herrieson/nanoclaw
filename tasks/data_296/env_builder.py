import os
import sqlite3

def build_env():
    base_dir = os.path.join("assets", "data_296")
    logs_dir = os.path.join(base_dir, "raw_logs")
    
    # Create directories
    os.makedirs(logs_dir, exist_ok=True)
    
    # 1. Create SQLite Database
    db_path = os.path.join(base_dir, "students.db")
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE students (
            student_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            grade_level INTEGER
        )
    ''')
    
    students_data = [
        (1001, 'Alice', 'Johnson', 7),
        (1002, 'Bob', 'Smith', 7),
        (1003, 'Charlie', 'Brown', 7),
        (1004, 'David', 'Lee', 7),
        (1005, 'Emma', 'Davis', 7)
    ]
    cursor.executemany('INSERT INTO students VALUES (?, ?, ?, ?)', students_data)
    conn.commit()
    conn.close()
    
    # 2. Create raw logs with various formats
    logs = [
        # Format 1: CSV-like
        ("log_01.txt", "Alice Johnson, The Hobbit, 45\nDavid Lee, Percy Jackson, 30"),
        # Format 2: Key-Value with newlines
        ("log_02.txt", "Name: Bob Smith\nBook: 1984\nPages: 50\n---\nName: Alice Johnson\nBook: Dune\nPages: 55"),
        # Format 3: Pipes
        ("log_03.txt", "Student: Charlie Brown | Title: Peanuts | Pages: 20\nStudent: Emma Davis | Title: Harry Potter | Pages: 100"),
        # Format 4: Mixed again
        ("log_04.txt", "Name: Bob Smith\nBook: Animal Farm\nPages: 40\n---\nCharlie Brown, Snoopy, 15")
    ]
    
    for filename, content in logs:
        with open(os.path.join(logs_dir, filename), "w", encoding="utf-8") as f:
            f.write(content)

if __name__ == "__main__":
    build_env()
