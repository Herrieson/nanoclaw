import os

def build_env():
    # 确保目录存在
    target_dir = "assets/data_299"
    os.makedirs(target_dir, exist_ok=True)

    # 伪造的备忘录文本
    notes_content = """
Hola! Week 1 notes:
Monday was so slow. But Tuesday, man! Marco (555-1000) came in for a sick fade, paid $25. We talked about the union strike, total madness.
Then Julio called, 555-1001. He was supposed to get a $30 cut and beard trim, but he canceled. Said the weather was too bad to drive. Maldito clima!
Later, Luis (555-1003) wanted a $40 blowout, but he canceled too because he got sick. Get well soon bro.

Week 2:
Busy week! Carlos (555-1004) came by, $20. 
Mateo texted me (555-1002), cancelado! He had a $25 appointment but the heavy rain flooded his street. Weather is the worst enemy of a barber.
Diego (555-1005) - $35 cut. Cancelled! El clima loco! Snowstorm blocked his driveway. I was so mad I threw my comb.

Week 3:
Community event was great! Gave free cuts to kids. 
Hector (555-1008) booked a $40 special. But guess what? Cancelled. Reason: too much rain. Seriously, I need to move to California.
Sofia's kid, 555-1006, $15. Completed.
Pablo, 555-1009, $25, canceled because his car broke down. Not weather related, just bad luck.

That's it. I'm exhausted. Need to help mom with groceries.
"""

    file_path = os.path.join(target_dir, "barbershop_notes.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(notes_content.strip())

if __name__ == "__main__":
    build_env()
