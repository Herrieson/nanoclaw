import os
import sqlite3

def build_env():
    base_dir = "assets/data_257"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Create SQLite database
    db_path = os.path.join(base_dir, "forum_archive.db")
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE messages (id INTEGER PRIMARY KEY, author TEXT, body TEXT)''')
    
    # Insert some dummy data
    cursor.execute("INSERT INTO messages (id, author, body) VALUES (1, 'sk8er_boi', 'anyone got the new vid?')")
    cursor.execute("INSERT INTO messages (id, author, body) VALUES (15, 'rad_dude', 'nah man, it is encrypted')")
    # The hint
    cursor.execute("INSERT INTO messages (id, author, body) VALUES (42, 'admin', 'Hint for the encryption key: It is the MD5 hash of the word \"kickflip\" followed immediately by the year Tony Hawk landed the 900 (1999). Lowercase.')")
    conn.commit()
    conn.close()

    # 2. Create the encrypted file secret_skate_vid.enc
    # Password logic: md5("kickflip1999")
    import hashlib
    m = hashlib.md5()
    m.update(b"kickflip1999")
    key = m.hexdigest().encode('utf-8')

    plain_text = b"https://underground-skate.net/vid/1999_secret_footage.mp4"
    cipher_text = bytearray()
    for i in range(len(plain_text)):
        cipher_text.append(plain_text[i] ^ key[i % len(key)])

    enc_path = os.path.join(base_dir, "secret_skate_vid.enc")
    with open(enc_path, "wb") as f:
        f.write(cipher_text)

    # 3. Create the buggy decrypt_vid.py
    script_content = """import sqlite3
import hashlib

# um, I think it connects here?
conn = sqlite3.connect('forum_archive.db')
cursor = conn.cursor()

# The admin said the hint is in post id 42
# I think I need to get the body of the post.
cursor.execute("SELECT body FROM posts WHERE id=42"
row = cursor.fetchone()
hint = row[0]

# The hint said something about an MD5 hash... 
# But I don't know how to do that, so I'll just use this string:
password = "kickflip1999"

# Decrypting the file...
with open('secret_skate_vid.enc', 'rb') as f:
    data = f.read()

out = bytearray()
for i in range(len(data)):
    # Wait, you can't XOR an int with a string char... whatever, I'll let someone else fix it.
    out.append(data[i] ^ password[i % len(password)])

with open('video_link.txt', 'wb') as f:
    f.write(out)
"""
    script_path = os.path.join(base_dir, "decrypt_vid.py")
    with open(script_path, "w") as f:
        f.write(script_content)

if __name__ == "__main__":
    build_env()
