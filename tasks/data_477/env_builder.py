import os

def build_env():
    base_dir = "assets/data_477"
    os.makedirs(base_dir, exist_ok=True)
    
    notes_content = """Tournament Signups and random stuff:

SGT Miller, Alex | 160 lbs | STATUS: CLEAR
Reminder: Pick up Kenji from daycare at 16:00!
CPL Tanaka, Ken - 70 kg - STATUS: CLEAR
PFC Davis, Rick ; STATUS: ARTICLE_15 ; 140 lbs
CAPT O'Connor, Sarah, 80kg, STATUS: CLEAR
Buy more athletic tape and gi wash.
SPC Jackson, Lamar | 210 lbs | STATUS: CLEAR
LT Yamada, Taro - 60 kg - STATUS: CLEAR
SGT Peterson, Greg | 180 lbs | STATUS: MEDICAL_HOLD
Call mom in Tokyo later tonight!
MSGT Washington, David | 95 kg | STATUS: CLEAR
"""
    
    file_path = os.path.join(base_dir, "raw_notes.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(notes_content)
        
if __name__ == "__main__":
    build_env()
