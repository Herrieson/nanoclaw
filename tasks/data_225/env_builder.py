import os

def build_env():
    base_dir = "assets/data_225"
    os.makedirs(base_dir, exist_ok=True)
    
    rsvps_content = """
>>> MESSAGE START
From: Sarah Jenkins
Date: Oct 12
Hey! I am so excited for the potluck. Put me down as attending! I'll bring my famous potato salad. No allergies here.
<<< MESSAGE END

====================
WebFormSub: Name=Elena Gomez; RSVP=Attending; Contribution=Vegan Tamales; Restrictions=Vegan, Peanuts
====================

Email from Principal Skinner:
Unfortunately, I cannot attend this year due to a district meeting. Have fun!

[SMS RECEIPT]
Sender: David K.
Message: Hey it's David, I'm coming! Bringing brownies. allergic to tree nuts.

>>> MESSAGE START
From: Mrs. Robinson (Room 204)
Subject: Re: Potluck
We will be there! I am bringing a huge Mac and Cheese. Dietary needs: Gluten-Free.
<<< MESSAGE END

Name: Mike T. | Status: Yes | Dish: Smoked Brisket | Dietary: None

Name: Lisa Simpson | Status: Not Attending | Dish: N/A | Dietary: Vegetarian

[SMS RECEIPT]
Sender: Chloe
Message: Omg so excited. Yes I'm coming. I'll bring a fruit salad. No restrictions.

WebFormSub: Name=Jamal Smith; RSVP=Attending; Contribution=Jollof Rice; Restrictions=halal
"""
    
    with open(os.path.join(base_dir, "potluck_rsvps.txt"), "w", encoding="utf-8") as f:
        f.write(rsvps_content.strip())

if __name__ == "__main__":
    build_env()
