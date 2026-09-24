import os
import argparse
import csv
import json

def build_turn_1():
    os.makedirs("registry", exist_ok=True)
    os.makedirs("guidelines", exist_ok=True)
    os.makedirs("submissions/batch_1", exist_ok=True)

    # 1. Registry
    with open("registry/students.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "grade"])
        writer.writerows([
            ["1001", "Alice", "9"],
            ["1002", "Bob", "10"],
            ["1003", "Carlos", "9"],
            ["1004", "Diana", "11"],
            ["1006", "Felix", "9"],
            ["1007", "Gloria", "10"]
        ])

    # 2. Guidelines
    rules = {
        "max_words": 45,
        "forbidden_themes": ["Politics", "Violence"],
        "cost_per_word": 0.10
    }
    with open("guidelines/rules.json", "w") as f:
        json.dump(rules, f, indent=4)

    # 3. Batch 1 Submissions
    poem_a = "ID: 1001\nTheme: Nature\n\nSunlight falls upon the quiet green meadow where wildflowers bloom in spring and gentle breezes carry the sweet scent of morning dew across the peaceful valley bringing endless joy today." # 30 words -> 3.0
    poem_b = "ID: 1002\nTheme: Politics\n\nElections are coming soon and the town is divided by angry voices shouting loudly over the broken promises of leaders." # 20 words -> Invalid theme
    poem_c = "ID: 1003\nTheme: Adventure\n\nMountains rise high above the clouds touching the endless sky with peaks of snow that shine brightly in the afternoon sun casting long shadows across the valley below where small rivers flow swiftly toward the distant ocean sparkling forever bright." # 40 words -> 4.0
    poem_d = "ID: 1004\nTheme: Sadness\n\nRain drops gently against the cold glass window while gray clouds fill the autumn sky bringing a soft quiet sadness to the empty street below as people hurry home escaping the sudden storm seeking warmth." # 35 words -> 3.5
    poem_e = "ID: 9999\nTheme: Joy\n\nDancing in the rain is fun and makes me feel alive with energy jumping through puddles splashing water everywhere laughing out loud." # 22 words -> Invalid ID

    with open("submissions/batch_1/poem_A.txt", "w") as f: f.write(poem_a)
    with open("submissions/batch_1/poem_B.txt", "w") as f: f.write(poem_b)
    with open("submissions/batch_1/poem_C.txt", "w") as f: f.write(poem_c)
    with open("submissions/batch_1/poem_D.txt", "w") as f: f.write(poem_d)
    with open("submissions/batch_1/poem_E.txt", "w") as f: f.write(poem_e)

def build_turn_2():
    os.makedirs("submissions/batch_2_spanish", exist_ok=True)

    # 1. Urgent Note (Budget limit)
    # Turn 1 accepted: 1001 (3.0), 1003 (4.0), 1004 (3.5). Total = 10.5.
    # New valid: 1006 (2.5). Total = 13.0.
    # Cap = 10.0. Will force dropping 1003 (4.0).
    with open("urgent_note.txt", "w") as f:
        f.write("ATTENTION: Due to recent school board budget cuts, the absolute maximum printing budget for the anthology is now capped at strictly $10.00. No exceptions.")

    # 2. Batch 2 Submissions
    poem_f = "ID: 1006\nTheme: Family\n\nBrothers and sisters gather around the warm fire sharing stories of old times laughing together as the cold night wind howls outside our safe home." # 25 words -> 2.5
    poem_g = "ID: 1007\nTheme: Violence\n\nSwords clashed in the dark bloody battle as brave warriors fought fiercely until the end." # 15 words -> Invalid theme

    with open("submissions/batch_2_spanish/poem_F.txt", "w") as f: f.write(poem_f)
    with open("submissions/batch_2_spanish/poem_G.txt", "w") as f: f.write(poem_g)

def build_turn_3():
    # 1. Scandal note
    # Forces dropping 1004 (Diana, 3.5). 
    # Current accepted pool was 1001 (3.0) + 1004 (3.5) + 1006 (2.5) = 9.0.
    # Dropping 1004 leaves 1001 (3.0) + 1006 (2.5) = 5.5.
    # Cap is 10.0. 1003 (4.0) was previously dropped, can now be re-added (5.5 + 4.0 = 9.5 <= 10.0).
    with open("scandal.txt", "w") as f:
        f.write("URGENT MEMO: Disciplinary Action.\n\nStudent ID 1004 has been caught plagiarizing online material. All their submissions must be completely voided from school publications immediately.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
    elif args.turn == 3:
        build_turn_3()
