import os

def build_env():
    base_dir = "assets/data_252"
    os.makedirs(base_dir, exist_ok=True)
    
    inbox_content = """
--- START OF MESSAGE ---
From: sarah.j@greenmail.com
Date: Oct 2
Subject: Volunteering!

Hey! I'm so excited for the Eco-Vision show. I'd love to volunteer. I've been doing a lot of upcycling lately and I have a large roll of Bamboo fabric I can bring for the design tables.
Best,
Sarah Jenkins
--- END OF MESSAGE ---

--- START OF MESSAGE ---
From: system@optometry-booking.local
Date: Oct 3
Subject: New Appointment: Oct 12

System Alert: 
New patient booking confirmed.
Date: Oct 12
Time: 10:00 AM
Patient Name: Robert Ford
Reason for visit: Routine eye exam and astigmatism check.
--- END OF MESSAGE ---

--- START OF MESSAGE ---
From: system@optometry-booking.local
Date: Oct 4
Subject: New Appointment: Oct 14

System Alert: 
New patient booking confirmed.
Date: Oct 14
Time: 2:30 PM
Patient Name: Emily Clark
Reason for visit: Contact lens fitting.
--- END OF MESSAGE ---

--- START OF MESSAGE ---
From: m.aurelius@ecothreads.org
Date: Oct 4
Subject: Re: Fabric Donation

Howdy! Happy to help out with the fashion show. I'll be there to volunteer. I managed to source some beautiful Organic Cotton from a local farm. 
See you there,
Marcus Aurelius
--- END OF MESSAGE ---

--- START OF MESSAGE ---
From: newsletter@sustainablefashionweekly.com
Date: Oct 5
Subject: Top 10 Hemp Designs This Fall!

Check out our latest article on why Hemp is taking over the runway!
(No action required, automated message)
--- END OF MESSAGE ---

--- START OF MESSAGE ---
From: system@optometry-booking.local
Date: Oct 6
Subject: New Appointment: Oct 12

System Alert: 
New patient booking confirmed.
Date: Oct 12
Time: 1:15 PM
Patient Name: William Abernathy
Reason for visit: Glaucoma screening.
--- END OF MESSAGE ---

--- START OF MESSAGE ---
From: chloe_designs@webmail.com
Date: Oct 7
Subject: Count me in

I'll be there to volunteer! I've got scraps of Recycled Polyester that are perfect for patchwork. 
- Chloe Price
--- END OF MESSAGE ---
"""
    
    with open(os.path.join(base_dir, "inbox_dump.txt"), "w") as f:
        f.write(inbox_content.strip())

if __name__ == "__main__":
    build_env()
