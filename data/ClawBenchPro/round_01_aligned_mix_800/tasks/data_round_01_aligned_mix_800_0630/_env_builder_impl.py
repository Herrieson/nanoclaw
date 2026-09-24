import os
import json

def build_env():
    # Create directories
    os.makedirs("raw_data", exist_ok=True)
    os.makedirs("sketches", exist_ok=True)
    os.makedirs("conference_materials", exist_ok=True)

    # Official roster
    roster = ["Luka Kovac", "Ana Horvat", "Marko Vidovic", "Petra Maric", "Ivan Peric"]
    with open("official_roster.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(roster))

    # Raw data - Grade 5 (Numeric and some duplicates)
    grade5_data = [
        {"name": "Luka Kovac", "math": 92, "science": 88},
        {"name": "Ana Horvat", "math": 76, "science": 82},
        {"name": "Unknown Entity", "math": 100, "science": 100}, # Anomaly
        {"name": "Luka Kovac", "math": 92, "science": 88}  # Duplicate
    ]
    with open("raw_data/grade5_records.json", "w", encoding="utf-8") as f:
        json.dump(grade5_data, f)

    # Raw data - Grade 6 (Letter grades and messy text)
    grade6_content = """Name,Subject,Score
Marko Vidovic,Math,A
Marko Vidovic,Science,B
Petra Maric,Math,C
Petra Maric,Science,D
Ivan Peric,Math,B
Ivan Peric,Science,A
Stranger danger,Math,F
"""
    with open("raw_data/grade6_scores.csv", "w", encoding="utf-8") as f:
        f.write(grade6_content)

    # Rubric sketch note
    rubric = """Notes for my sketches:
Standard Conversion for letter grades:
A -> 95
B -> 85
C -> 75
D -> 65
F -> 50
If average < 70, flag as 'Needs Attention'.
Discard any student not in my official roster list.
"""
    with open("sketches/rubric.txt", "w", encoding="utf-8") as f:
        f.write(rubric)

if __name__ == "__main__":
    build_env()
