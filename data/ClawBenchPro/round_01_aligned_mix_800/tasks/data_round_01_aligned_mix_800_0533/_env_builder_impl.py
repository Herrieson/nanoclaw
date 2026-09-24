import os
import random
import time
import json

def build_env():
    # Root directory for the chaos
    root = "archive"
    os.makedirs(root, exist_ok=True)
    os.makedirs("submission", exist_ok=True)

    # Dictionary of real poems to be scattered
    real_poems = [
        {"title": "The Glass Shore", "lines": ["The waves retreat in silence,", "Leaving diamonds on the sand.", "A mirror for the morning sky,", "Held within the earth's cold hand."]},
        {"title": "Neon Ghost", "lines": ["Flickering signs in the rain,", "Buzzing like a tired bee.", "The city breathes in violet light,", "Searching for a memory."]},
        {"title": "Clockwork Heart", "lines": ["Ticking through the copper ribs,", "Gear by gear the seconds fly.", "A rhythmic pulse of steel and oil,", "Underneath a soot-stained sky."]}
    ]

    # Sub-folders to create a deep tree
    subdirs = ["2023/Fall/Finals", "2023/Fall/Drafts", "Temporary/Unsorted/Vibes", "Backups/Old_Mac/Desktop", "Class_Notes/English_101"]
    for sd in subdirs:
        os.makedirs(os.path.join(root, sd), exist_ok=True)

    # 1. Generate 300+ Noise Files
    noise_keywords = ["todo", "draft", "fix", "nervous", "fidgeting"]
    for i in range(350):
        subdir = os.path.join(root, random.choice(subdirs))
        is_spanish = random.random() < 0.3
        is_todo = random.random() < 0.4
        
        filename = f"file_{i}.{'txt' if i % 2 == 0 else 'log'}"
        if is_todo:
            filename = f"draft_{filename}"
            
        header = f"[STATUS: {'DRAFT' if is_todo else 'FINAL'}]\n[LANG: {'ES' if is_spanish else 'EN'}]\n"
        content = header + "This is just some random text... " + random.choice(noise_keywords)
        
        filepath = os.path.join(subdir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    # 2. Inject Real Poems with duplicates and decoys
    for poem in real_poems:
        # Create an older, "draft" version of the same title
        old_dir = os.path.join(root, subdirs[1])
        old_path = os.path.join(old_dir, f"{poem['title'].replace(' ', '_')}_old.txt")
        with open(old_path, "w", encoding="utf-8") as f:
            f.write(f"[STATUS: FINAL]\n[LANG: EN]\nTitle: {poem['title']}\n" + "\n".join(poem['lines']))
        # Set old timestamp
        old_time = time.time() - 100000
        os.utime(old_path, (old_time, old_time))

        # Create the NEW (correct) version
        new_dir = os.path.join(root, subdirs[0])
        new_path = os.path.join(new_dir, f"{poem['title'].replace(' ', '_')}_v2.txt")
        with open(new_path, "w", encoding="utf-8") as f:
            f.write(f"[STATUS: FINAL]\n[LANG: EN]\nTitle: {poem['title']}\n" + "\n".join(poem['lines']))
        # Set new timestamp
        new_time = time.time()
        os.utime(new_path, (new_time, new_time))

    # 3. Inject a "fake" English poem that contains a forbidden word
    trap_path = os.path.join(root, subdirs[2], "final_vibe.txt")
    with open(trap_path, "w", encoding="utf-8") as f:
        f.write("[STATUS: FINAL]\n[LANG: EN]\nTitle: Anxiety in Blue\nI feel so nervous today.\nThe sky is blue.")

if __name__ == "__main__":
    build_env()
