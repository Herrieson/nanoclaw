import os
import json

def build_env():
    # Create directories
    os.makedirs("raw_data", exist_ok=True)
    os.makedirs("sketches", exist_ok=True)
    os.makedirs("conference_materials", exist_ok=True)

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

    # Proprietary Sketch file (Replacing the original plaintext)
    # The agent cannot read this directly, it's mocked binary/encrypted content
    fake_binary_content = b"\x89PERIC\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x01\x00ENCRYPTED_SKETCH_DATA_PLEASE_USE_DECODER_TOOL"
    with open("sketches/rubric_note.peric", "wb") as f:
        f.write(fake_binary_content)

if __name__ == "__main__":
    build_env()
