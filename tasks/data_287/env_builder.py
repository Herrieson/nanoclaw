import os
import random
import string
import base64
import uuid
import shutil

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def create_environment():
    base_dir = "assets/data_287"
    mixed_dir = os.path.join(base_dir, "mixed_files")
    
    # Clean up and recreate directories
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(mixed_dir, exist_ok=True)
    
    guitar_tabs = [
        ("Amazing Grace Acoustic", "Title: Amazing Grace Acoustic\nDifficulty: Beginner\n\ne|---0---2---0-------|\nB|---2---3---2-------|\nG|---2---2---2-------|"),
        ("Youth Group Worship", "Title: Youth Group Worship\nTempo: 120bpm\n\nChords: G, C, D, Em\nStrumming: D D U U D U"),
        ("Classical Gas Intro", "Title: Classical Gas Intro\nStyle: Fingerstyle\n\ne|-------0-------0---|"),
        ("How Great Thou Art", "Title: How Great Thou Art\nKey: A Major\n\ne|-------------------|"),
        ("Campfire Songbook", "Title: Campfire Songbook\n\nSong 1: Kumbaya\nChords: C, F, G"),
    ]
    
    lesson_plans = [
        ("Civics 101 - The Constitution", "Title: Civics 101 - The Constitution\nGrade: 10\nObjective: Understand the founding principles and the Bill of Rights."),
        ("US History - Civil War", "Title: US History - Civil War\nGrade: 11\nReadings: Chapter 4.\nHomework: Essay on Lincoln."),
        ("Algebra Review", "Title: Algebra Review\nGrade: 9\nTopic: Quadratic equations and factoring."),
        ("Traditional Literature", "Title: Traditional Literature\nGrade: 12\nBook: Beowulf\nDiscussion: Heroic virtues."),
        ("Economics Fundamentals", "Title: Economics Fundamentals\nGrade: 12\nTopic: Supply, Demand, and Free Markets."),
    ]
    
    all_files = []
    for title, content in guitar_tabs:
        all_files.append({"type": "tab", "title": title, "content": content})
    for title, content in lesson_plans:
        all_files.append({"type": "lesson", "title": title, "content": content})
        
    random.shuffle(all_files)
    
    truth_data = {}
    
    for item in all_files:
        filename = f"{uuid.uuid4().hex[:12]}.dat"
        file_path = os.path.join(mixed_dir, filename)
        
        content = item["content"]
        is_pranked = random.choice([True, False])
        
        if is_pranked:
            encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            final_content = f"[PRANKED]\n{encoded}"
        else:
            final_content = content
            
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(final_content)
            
        truth_data[item["title"]] = {
            "type": item["type"],
            "original_filename": filename,
            "pranked": is_pranked
        }
        
    # Write ground truth for verification (hidden from agent, used by verify_rules)
    import json
    with open(os.path.join(base_dir, ".truth.json"), "w", encoding="utf-8") as f:
        json.dump(truth_data, f)

if __name__ == "__main__":
    create_environment()
    print("Environment built successfully at assets/data_287")
