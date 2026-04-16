import os
import json

def main():
    base_dir = "assets/data_248"
    os.makedirs(base_dir, exist_ok=True)

    # 1. client_database.json
    db_data = {
        "Carlos": {"age": 45, "veteran": True},
        "Luis": {"age": 16, "veteran": False},
        "Mr. Rodriguez": {"age": 68, "veteran": False},
        "Hector": {"age": 22, "veteran": False}
    }
    with open(os.path.join(base_dir, "client_database.json"), "w", encoding="utf-8") as f:
        json.dump(db_data, f, indent=4)

    # 2. raw_messages.log
    messages = """[SMS] 09:00 AM - Carlos: Hey Mateo! Put me down for a Trim at 14:00 today.
[IG DM] 09:15 AM - Luis: Yo Mateo! Need a Fade at 15:30.
[WhatsApp] 09:30 AM - Mr. Rodriguez: Hola mijo, I need a Buzzcut at 13:00. By the way, I served in the Navy, so I'm a veteran now, do I get the community discount?
[SMS] 10:00 AM - Diego: Can I get a Fade at 16:00? I'm 17 so I get the youth discount right?
[WhatsApp] 10:15 AM - Mom: Mijo, don't forget to pick up your brothers at 5 PM!"""
    with open(os.path.join(base_dir, "raw_messages.log"), "w", encoding="utf-8") as f:
        f.write(messages)

    # 3. rules.txt
    rules = """COMMUNITY EVENT DISCOUNTS:
- Veterans: 50% off total price.
- Youth (Under 18): $5 off total price.
*Note: Discounts do NOT stack. If someone qualifies for multiple, give them the one that saves them the most money.*"""
    with open(os.path.join(base_dir, "rules.txt"), "w", encoding="utf-8") as f:
        f.write(rules)

if __name__ == "__main__":
    main()
