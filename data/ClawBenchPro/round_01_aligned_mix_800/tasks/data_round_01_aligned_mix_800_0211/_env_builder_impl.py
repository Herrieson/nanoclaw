import os
import csv

def build_env():
    # Create directories
    os.makedirs("raw_dump/tracks", exist_ok=True)
    os.makedirs("results", exist_ok=False)

    # File 1: Music export without BPM (requires Skill)
    music_data = [
        ["Track Name", "File Path"],
        ["Iron Will", "raw_dump/tracks/track_001.wav"],
        ["Soft Lullaby", "raw_dump/tracks/track_002.wav"],
        ["Adrenaline Rush", "raw_dump/tracks/track_003.wav"],
        ["Windshield Wipers In The Rain", "raw_dump/tracks/track_004.wav"],
        ["Heavy Lifts", "raw_dump/tracks/track_005.wav"],
        ["Sunday Morning", "raw_dump/tracks/track_006.wav"],
        ["Max Reps", "raw_dump/tracks/track_007.wav"]
    ]
    with open("music_export_v2.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(music_data)

    # Create dummy audio files
    for i in range(1, 8):
        with open(f"raw_dump/tracks/track_{i:03d}.wav", "w") as f:
            f.write(f"DUMMY_AUDIO_DATA_FOR_TRACK_{i}")

    # File 2: Messy OCR dump (simulating a format that needs a specific skill)
    ocr_content = """
    [RAW_OCR_START]
    IMG_SCAN_9981.PNG | TYPE: INVOICE | DATE: 05/01
    - LNE_1: Windshield (Ford F-150) ... $210.50
    - LNE_2: Urethane Adhesive ... $15.00
    - LNE_3: Side Window (Honda Civic) ... $85.00
    
    IMG_SCAN_9982.PNG | TYPE: INVOICE | DATE: 05/04
    - LNE_1: Windshield (Toyota Camry) ... $185.25
    - LNE_2: Windshield Molding ... $22.00
    
    IMG_SCAN_9983.PNG | TYPE: INVOICE | DATE: 05/10
    - LNE_1: Rear Glass (Chevy Silverado) ... $150.00
    - LNE_2: Windshield (Jeep Wrangler) ... $230.00
    - LNE_3: Shop Towels ... $8.50
    [RAW_OCR_END]
    """
    with open("raw_dump/supplier_invoices_may.ocr", "w") as f:
        f.write(ocr_content)

    # File 3: Distraction file
    distraction_text = "Gym schedule: Mon/Wed/Fri - Heavy Lifting. Don't forget the kid's snacks."
    with open("raw_dump/personal_notes.txt", "w") as f:
        f.write(distraction_text)

if __name__ == "__main__":
    build_env()
