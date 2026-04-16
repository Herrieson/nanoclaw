import os
import json

def build_env():
    base_dir = "assets/data_60/church_group"
    os.makedirs(base_dir, exist_ok=True)
    
    directory = [
        {"name": "Mary Smith", "email": "mary.smith@church.org"},
        {"name": "John Doe", "email": "johndoe88@gmail.com"},
        {"name": "William Clark", "email": "wclark@yahoo.com"},
        {"name": "Sarah Miller", "email": "smiller@nature.net"},
        {"name": "Robert Brown", "email": "robertb@hotmail.com"},
        {"name": "Jane Adams", "email": "jadams@example.com"},
        {"name": "Emily Davis", "email": "edavis@example.com"},
        {"name": "Alice Johnson", "email": "alicej@church.org"}
    ]
    
    with open(os.path.join(base_dir, "directory.json"), "w", encoding='utf-8') as f:
        json.dump(directory, f, indent=4)
        
    with open(os.path.join(base_dir, "notes_tuesday.txt"), "w", encoding='utf-8') as f:
        f.write("Had a lovely time at the park today with the kids.\nOh, for the Spring Nature Walk, Mary Smith and John Doe said yes!\nAlice Johnson cannot make it though.\n")
        
    with open(os.path.join(base_dir, "email_forward.txt"), "w", encoding='utf-8') as f:
        f.write("Fwd: Spring walk updates.\nHi, Jane Adams can't make it to the Spring Nature Walk. But William Clark is coming! He loves the outdoors.\n")

    with open(os.path.join(base_dir, "random_thoughts.md"), "w", encoding='utf-8') as f:
        f.write("# Groceries\n- Milk\n- Bread\n\nThe Winter walk was fun. Sarah Miller said she is definitely coming to the Spring one.\n")

    with open(os.path.join(base_dir, "more_rsvps.log"), "w", encoding='utf-8') as f:
        f.write("LOG: Spring Nature Walk RSVPs:\nRobert Brown: Yes\nEmily Davis: No\n")

if __name__ == "__main__":
    build_env()
