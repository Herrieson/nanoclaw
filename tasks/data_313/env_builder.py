import os
import csv

def build_env():
    base_dir = "assets/data_313"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Create signups.csv
    csv_path = os.path.join(base_dir, "signups.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Name', 'Email', 'Role_Preference'])
        writer.writerow(['101', 'Emily Clark', 'emily.c@example.com', 'Runway Coordinator'])
        writer.writerow(['102', 'Michael Torres', 'mike.t@example.com', 'Usher'])
        writer.writerow(['103', 'Sarah Jenkins', 's.jenkins@example.com', 'Wardrobe Assistant'])
        writer.writerow(['104', 'David Kim', 'dkim99@example.com', 'Lighting Technician'])
        writer.writerow(['105', 'Jessica Alba', 'jess.a@example.com', 'Makeup Artist'])
        writer.writerow(['106', 'Tom Hardy', 'tommyh@example.com', 'Usher'])
        writer.writerow(['107', 'Chloe Price', 'chloe.p@example.com', 'Guest Registration'])

    # 2. Create orientation_attendance.txt
    # Notice: Tom Hardy and Chloe Price missed orientation.
    attendance_path = os.path.join(base_dir, "orientation_attendance.txt")
    with open(attendance_path, 'w', encoding='utf-8') as f:
        f.write("Orientation Session - Fall Charity Gala\n")
        f.write("Attendees:\n")
        f.write("- Emily Clark\n")
        f.write("- Michael Torres\n")
        f.write("- Sarah Jenkins\n")
        f.write("- David Kim\n")
        f.write("- Jessica Alba\n")
        f.write("- Marcus Johnson (Staff)\n")

    # 3. Create email_updates.log
    # Sarah cancels. Michael changes role.
    log_path = os.path.join(base_dir, "email_updates.log")
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write("""--- EMAIL SERVER BACKUP ---
Date: Tuesday 10:00 AM
From: Sarah Jenkins <s.jenkins@example.com>
Subject: Re: Gala!
Hey there! I am so, so sorry but I have a family emergency and have to cancel my volunteering this weekend. I feel terrible about this. Good luck with the fashion show!

Date: Wednesday 2:15 PM
From: Michael Torres <mike.t@example.com>
Subject: Role change request
Hi! Is it possible for me to switch from Usher to Wardrobe Assistant? I have a real passion for styling and would love to be backstage. Thanks!

Date: Thursday 9:00 AM
From: Emily Clark <emily.c@example.com>
Subject: Excited!
Just wanted to say I can't wait for Saturday. See you then!
""")

if __name__ == "__main__":
    build_env()
