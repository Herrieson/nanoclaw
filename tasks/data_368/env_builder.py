import os

def create_environment():
    base_dir = "assets/data_368"
    journals_dir = os.path.join(base_dir, "journals")
    
    os.makedirs(journals_dir, exist_ok=True)
    
    # Journal entries reflecting the persona's lack of education, southern accent, 
    # and anxiety. The target pattern: Buster appears most on Thursday, in Rain.
    journals = {
        "log_01.txt": "Mondy. Sun is beatin down hot today. Saw a couple herons down by the water. Nothin much else to report. Mindin my own business.",
        "log_02.txt": "Tuesdee. Mighty cloudy. Wind is pickin up. I stayed inside mostly, reading a bit. Heard some rustlin but it was just a coon.",
        "log_03.txt": "Thursdy. Rainin' cats and dogs! Lord Almighty, Buster was right up on the porch! Scared the livin daylights outta me. I locked the door real quick.",
        "log_04.txt": "Fridy. Sunny again. Went for a walk in the woods. Ain't no government man gonna tell me where I can walk. Peaceful today.",
        "log_05.txt": "Sundee. Pourin rain. Didn't see hide nor hair of any gators today, thank heavens.",
        "log_06.txt": "Thursday. Keepin it short today. It's pouring down rain. Looked out the window and that darn Buster was watchin me from the puddle. Got my heart racing.",
        "log_07.txt": "Wednesdy. Clear skies, very sunny. Caught a fish. Good day.",
        "log_08.txt": "Thursdee. Rain is fallin hard. Buster snapped at my boot when I went to get firewood! I swear that beast has it out for me.",
        "log_09.txt": "Mondy. Just rain today. Boring day. Read my book.",
        "log_10.txt": "Saturdee. Sunny and warm. Buster was sunbathin' on the bank. Kept my distance. He didn't seem to care I was there, but I don't trust him.",
        "log_11.txt": "Thursdy. Rainin again. Why does it always rain? Seen Buster lookin at me from the reeds. I'm stayin inside till it stops.",
        "log_12.txt": "Tuesdy. Cloudy, looks like it might storm later. No gators today."
    }
    
    for filename, content in journals.items():
        with open(os.path.join(journals_dir, filename), "w") as f:
            f.write(content)

if __name__ == "__main__":
    create_environment()
