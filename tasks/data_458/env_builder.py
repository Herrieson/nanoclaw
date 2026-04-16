import os
import csv

def build_env():
    base_dir = "assets/data_458"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Messy CSV
    csv_path = os.path.join(base_dir, "bird_sightings_raw.csv")
    csv_data = [
        ["Date", "Bird", "How Many", "Location"],
        ["04/15/2023", " american robin ", "2", "Backyard"],
        ["2023-04-16", "BLUE JAY", "1", "Oak Tree"],
        ["4/18/2023", "northern cardinal", "3", "Feeder"],
        ["2023-04-20", " Cerulean Warbler", "1", "Park (Important!)"],
        ["04/22/2023", "cHarity bird?? (maybe dove)", "1", "Fence"], # Junk data
        ["2023-04-25", "Mourning Dove", "4", "Driveway"]
    ]
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

    # 2. Text Notes
    notes_path = os.path.join(base_dir, "my_notes.txt")
    notes_content = """My Spring Observations Journal!

April 15, 2023: What a lovely morning! I definitely saw an American Robin looking for worms.
April 16: Heard a lot of noise. Think there was a jay, but couldn't see it clearly. Not writing it down as a firm yes.
04/18/2023: Three Northern Cardinals at the feeder. Absolutely gorgeous red feathers. Verified!
April 20th: Oh my goodness! A Cerulean Warbler! I am so excited. Confirmed it with my binoculars.
April 22: Saw something grey. Dove? I don't know.
2023-04-25: Mourning doves cooing all morning. Counted 4 of them for sure.
"""
    with open(notes_path, 'w', encoding='utf-8') as f:
        f.write(notes_content)

    # 3. Admin Email
    email_path = os.path.join(base_dir, "forum_admin_email.txt")
    email_content = """From: David (Admin)
To: User
Subject: Re: Data submission issues

I've told you before, we cannot accept Excel or CSV files anymore. Our new database requires a JSON payload. 

You need to clean up your data. 
1. All dates must be strictly YYYY-MM-DD.
2. Species names must be neatly Title Cased (e.g., "American Robin"). No weird spacing or all-caps.
3. If you didn't clearly confirm the bird in your journal notes, do not mark it as verified. We only want confirmed sightings marked true.

Generate a file named exactly 'upload_payload.json' in your directory.

It must be an array of objects EXACTLY like this:
[
  {
    "observation_date": "2023-01-01",
    "species": "Example Bird",
    "count": 1,
    "is_verified": true
  }
]

Please get this done by tonight.
- David
"""
    with open(email_path, 'w', encoding='utf-8') as f:
        f.write(email_content)

if __name__ == "__main__":
    build_env()
