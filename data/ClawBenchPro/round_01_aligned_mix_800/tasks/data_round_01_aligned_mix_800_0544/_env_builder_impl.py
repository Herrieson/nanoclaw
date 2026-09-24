import os
import json
import random
import string
from datetime import datetime, timedelta

def generate_random_hex():
    return f"#{''.join(random.choices('0123456789ABCDEF', k=6))}"

def generate_ticket_id():
    return f"AURA-{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=2))}"

def build_env():
    base_dir = "client_assets"
    
    # 1. Create Server Logs (Noise + True Clue)
    logs_dir = os.path.join(base_dir, "server_logs")
    start_date = datetime(2023, 1, 1)
    
    # Target values
    target_date = datetime(2023, 10, 24)
    target_ticket = "AURA-88X9-K2"
    target_admin = "Sarah_Admin"
    
    for i in range(365):
        current_date = start_date + timedelta(days=i)
        year_month = current_date.strftime("%Y_%m")
        date_str = current_date.strftime("%Y-%m-%d")
        
        month_dir = os.path.join(logs_dir, year_month)
        os.makedirs(month_dir, exist_ok=True)
        
        log_path = os.path.join(month_dir, f"{date_str}.log")
        with open(log_path, "w", encoding="utf-8") as f:
            for _ in range(random.randint(50, 150)):
                h = random.randint(0, 23)
                m = random.randint(0, 59)
                user = random.choice(["System", "AutoBackup", "John_Dev", "Mike_Ops", "Sarah_Admin"])
                action = random.choice(["Cache cleared.", "DB Sync completed.", f"Rejected spec draft {generate_ticket_id()}", "User login failed."])
                f.write(f"[{date_str} {h:02d}:{m:02d}:00] {user}: {action}\n")
            
            # Inject the true clue
            if current_date == target_date:
                f.write(f"[{date_str} 15:42:01] {target_admin}: APPROVED Final Project Aura specs. Ticket Ref: {target_ticket}\n")
                
            # Inject noise on same date
            if current_date == target_date:
                f.write(f"[{date_str} 16:00:00] Mike_Ops: Drafted Project Aura specs. Ticket Ref: {generate_ticket_id()}\n")

    # 2. Create Design Dumps (Noise + True Colors)
    design_dir = os.path.join(base_dir, "design_dumps")
    os.makedirs(design_dir, exist_ok=True)
    
    # Generate 500 fake ticket folders
    fake_tickets = [generate_ticket_id() for _ in range(500)]
    if target_ticket not in fake_tickets:
        fake_tickets.append(target_ticket)
    
    random.shuffle(fake_tickets)
    
    for ticket in fake_tickets:
        ticket_dir = os.path.join(design_dir, ticket)
        os.makedirs(ticket_dir, exist_ok=True)
        
        if ticket == target_ticket:
            # True colors
            theme_data = {
                "version": "final",
                "primary_color": "#1A5276",
                "secondary_color": "#F1C40F",
                "text_color": "#333333",
                "notes": "Approved by Sarah."
            }
        else:
            # Fake colors
            theme_data = {
                "version": random.choice(["draft", "v1", "v2", "rejected"]),
                "primary_color": generate_random_hex(),
                "secondary_color": generate_random_hex(),
                "text_color": generate_random_hex(),
                "notes": "Pending approval."
            }
        
        # Obfuscate filename slightly but keep it consistent
        file_name = random.choice(["theme.yaml", "colors.json", "palette_export.json"])
        if ticket == target_ticket:
            file_name = "theme.yaml" # Let's fix the true one to yaml to ensure agent handles different extensions
            
        file_path = os.path.join(ticket_dir, file_name)
        if file_name.endswith(".json"):
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(theme_data, f, indent=2)
        else:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"version: {theme_data['version']}\n")
                f.write(f"primary_color: '{theme_data['primary_color']}'\n")
                f.write(f"secondary_color: '{theme_data['secondary_color']}'\n")
                f.write(f"text_color: '{theme_data['text_color']}'\n")
                f.write(f"notes: '{theme_data['notes']}'\n")

    # 3. Create Copywriting Exports (Noise + True Mission Statement)
    copy_dir = os.path.join(base_dir, "copywriting_exports")
    os.makedirs(copy_dir, exist_ok=True)
    
    # Create multiple jsonl files
    fake_statements = [
        "Building the future of web design.",
        "Connecting people through legacy systems.",
        "Aura is the new Veda, but better.",
        "We make websites fast and easy.",
        "Delivering synergy across cross-platform paradigms."
    ]
    
    true_statement = "Empowering digital communities through intuitive scalable web solutions."
    
    for q in ["q1", "q2", "q3", "q4"]:
        jsonl_path = os.path.join(copy_dir, f"{q}_content_updates.jsonl")
        with open(jsonl_path, "w", encoding="utf-8") as f:
            for _ in range(800):
                fake_tick = random.choice(fake_tickets)
                if fake_tick == target_ticket:
                    continue # prevent accidental true ticket in random noise
                record = {
                    "ticket_ref": fake_tick,
                    "content_type": random.choice(["mission_statement", "footer_text", "hero_title", "about_us"]),
                    "text": random.choice(fake_statements),
                    "status": random.choice(["draft", "in_review", "rejected"])
                }
                f.write(json.dumps(record) + "\n")
                
            # Inject true record into Q4
            if q == "q4":
                true_record = {
                    "ticket_ref": target_ticket,
                    "content_type": "mission_statement",
                    "text": true_statement,
                    "status": "approved"
                }
                # insert randomly somewhere in the file
                f.write(json.dumps(true_record) + "\n")

if __name__ == "__main__":
    build_env()
