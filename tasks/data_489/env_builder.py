import os
import json

def caesar_cipher(text, shift):
    result = ""
    for char in text:
        if char.isalpha():
            ascii_offset = 65 if char.isupper() else 97
            result += chr((ord(char) - ascii_offset + shift) % 26 + ascii_offset)
        else:
            result += char
    return result

def build_env():
    base_dir = "assets/data_489"
    archive_dir = os.path.join(base_dir, "archives")
    
    os.makedirs(archive_dir, exist_ok=True)
    
    # Create notes
    notes_content = """Digitization Notes - Dr. Vance
Date: Oct 12

I've finally finished scanning the 1954 batch. As a reminder for the lecture, the opposition used a rather elementary substitution method back then. To maintain historical accuracy in my demonstration, I noted that they used a standard Caesar shift of 5 for these tactical transmissions.

I need to make sure the kids' soccer cleats are in the car before I leave today.
"""
    with open(os.path.join(base_dir, "notes.txt"), "w") as f:
        f.write(notes_content)
        
    # Create plain text cables
    cable_1 = """STATUS: CLEAR
DATE: 1954-03-12
BODY: Weather conditions optimal for the drop. Operative REDBIRD is in position.
"""
    with open(os.path.join(archive_dir, "cable_1954_03_12.txt"), "w") as f:
        f.write(cable_1)

    cable_2 = """STATUS: CLEAR
DATE: 1954-04-01
BODY: Resupply delayed. Do not contact Operative BLUEJAY until further notice.
"""
    with open(os.path.join(archive_dir, "cable_1954_04_01.txt"), "w") as f:
        f.write(cable_2)

    # Create encrypted cables
    # Target Operatives: NIGHTHAWK, SILVERFOX, IRONBEAR
    enc_body_1 = "The package has been secured. OPERATIVE: NIGHTHAWK will proceed to the extraction point."
    cable_3 = f"""STATUS: ENCRYPTED
DATE: 1954-05-15
BODY: {caesar_cipher(enc_body_1, 5)}
"""
    with open(os.path.join(archive_dir, "cable_1954_05_15.txt"), "w") as f:
        f.write(cable_3)

    enc_body_2 = "Compromise detected in sector 4. OPERATIVE: SILVERFOX is burning documents. OPERATIVE: IRONBEAR is providing cover."
    cable_4 = f"""STATUS: ENCRYPTED
DATE: 1954-06-22
BODY: {caesar_cipher(enc_body_2, 5)}
"""
    with open(os.path.join(archive_dir, "cable_1954_06_22.txt"), "w") as f:
        f.write(cable_4)

if __name__ == "__main__":
    build_env()
