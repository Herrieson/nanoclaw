import os
import sqlite3
import csv

def build():
    base_dir = "assets/data_285/client_project"
    os.makedirs(os.path.join(base_dir, "raw_pages"), exist_ok=True)
    
    # 1. HTML pages
    pages = [
        {"username": "anil_85", "text": "Very good quality, will buy again.", "file": "page1.html"},
        {"username": "sneha_rao", "text": "Not what I expected.", "file": "page2.html"},
        {"username": "john_d", "text": "Absolutely fantastic service!", "file": "page3.html"},
        {"username": "priya_k", "text": "Looks nice, might buy.", "file": "page4.html"},
        {"username": "raj_kumar", "text": "Five stars, prompt delivery.", "file": "page5.html"}
    ]
    
    for p in pages:
        html_content = f"""<!DOCTYPE html>
<html>
<head><title>User Testimonial</title></head>
<body>
    <h1>User Feedback</h1>
    <div class="sidebar">Advertisement Block</div>
    <div class="testimonial-block">
        <span class="author" data-username="{p['username']}">User Name</span>
        <p class="content">{p['text']}</p>
    </div>
    <footer>Copyright 2023</footer>
</body>
</html>"""
        with open(os.path.join(base_dir, "raw_pages", p['file']), "w", encoding="utf-8") as f:
            f.write(html_content)
            
    # 2. SQLite DB
    db_path = os.path.join(base_dir, "users.db")
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, email TEXT)")
    users = [
        ("anil_85", "anil@mumbai.in"),
        ("sneha_rao", "sneha@rao.com"),
        ("john_d", "john@doe.com"),
        ("priya_k", "priya.k@domain.com"),
        ("raj_kumar", "raj@kumar.net")
    ]
    cursor.executemany("INSERT INTO users (username, email) VALUES (?, ?)", users)
    conn.commit()
    conn.close()
    
    # 3. CSV File
    csv_path = os.path.join(base_dir, "purchase_records.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["TransactionID", "CustomerEmail", "Status"])
        writer.writerow(["TX1001", "anil@mumbai.in", "purchased"])
        writer.writerow(["TX1002", "sneha@rao.com", "refunded"])
        writer.writerow(["TX1003", "john@doe.com", "purchased"])
        writer.writerow(["TX1004", "priya.k@domain.com", "cart"])
        writer.writerow(["TX1005", "raj@kumar.net", "purchased"])

if __name__ == "__main__":
    build()
