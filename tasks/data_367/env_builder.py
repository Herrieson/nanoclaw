import os
import json
import random

def build_env():
    base_dir = "assets/data_367"
    raw_dir = os.path.join(base_dir, "raw_data")
    
    os.makedirs(raw_dir, exist_ok=True)
    
    publishers = ["Marvel", "DC", "Image", "Dark Horse", "IDW"]
    heroes = ["Spider-Man", "Batman", "Spawn", "Hellboy", "TMNT", "X-Men", "Superman", "Invincible"]
    
    valid_count = 0
    
    # Generate JSON files
    for i in range(40):
        pub = random.choice(publishers)
        title = f"The Amazing {random.choice(heroes)}"
        issue = random.randint(1, 150)
        
        data = {
            "comic_title": title,
            "issue_no": str(issue),
            "pub": pub,
            "notes": "Mint condition" if random.random() > 0.5 else "Slight tear on cover"
        }
        
        with open(os.path.join(raw_dir, f"export_{i}.json"), "w") as f:
            json.dump(data, f)
        valid_count += 1
            
    # Generate TXT files
    for i in range(40, 80):
        pub = random.choice(publishers)
        title = f"Uncanny {random.choice(heroes)}"
        issue = random.randint(1, 500)
        
        content = f"Title: {title}\nIssue: {issue}\nPublisher: {pub}\nCondition: Good\nRead: Yes\n"
        
        with open(os.path.join(raw_dir, f"notes_{i}.txt"), "w") as f:
            f.write(content)
        valid_count += 1
            
    # Generate Junk files
    for i in range(80, 100):
        content = "Remember to buy milk.\nDo math homework chapter 4.\nAsk Dave about his World of Warcraft account."
        if i % 2 == 0:
            with open(os.path.join(raw_dir, f"junk_{i}.txt"), "w") as f:
                f.write(content)
        else:
            with open(os.path.join(raw_dir, f"junk_{i}.json"), "w") as f:
                json.dump({"random_thought": content, "timestamp": "2023-10-10"}, f)

    # Save expected count for verification
    with open(os.path.join(base_dir, "expected_meta.json"), "w") as f:
        json.dump({"expected_valid_rows": valid_count}, f)

if __name__ == "__main__":
    build_env()
