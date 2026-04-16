import os

def main():
    base_dir = "assets/data_346"
    os.makedirs(base_dir, exist_ok=True)

    raw_dump_content = """=== RSVP LOG START ===

Date: 2023-10-01
Name: Sarah Jenkins
Contact: sarahj@eco.org
Message: So excited for the swap! I'm bringing 5 old jeans for the upcycle bin!

--------------------
Date: 2023-10-02
Name: Mike Thompson
Email: mike99 at gmail dot com
Message: Hey, I have some shirts and 2 pairs of denim pants. See ya.

--------------------
Date: 2023-10-02
User: jessica_w
Contact: jess.w@hotmail.com
Message: Bringing lots of dresses, probably about 12 items. No denim though, sorry!

--------------------
Date: 2023-10-03
Name: Alex B.
Email: alex.b(at)yahoo(dot)com
Message: 3 items. Jackets and jeans. Can't wait to learn about sustainable fashion.

--------------------
Date: 2023-10-04
Name: Samantha Smith
Contact: s.smith@yahoo.com
Message: Will bring 10 items (all cotton tees).

--------------------
Date: 2023-10-05
Name: Chloe Adams
Email: chloe.eco at mail.com
Message: I've got 4 pairs of JEANS that need a new life!

=== RSVP LOG END ===
"""
    
    file_path = os.path.join(base_dir, "rsvps_raw_dump.txt")
    with open(file_path, "w") as f:
        f.write(raw_dump_content)

if __name__ == "__main__":
    main()
