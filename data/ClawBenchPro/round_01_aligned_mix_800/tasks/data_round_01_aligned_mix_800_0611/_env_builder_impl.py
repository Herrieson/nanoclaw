import os
import csv

def build_env():
    os.makedirs("raw_dump", exist_ok=True)

    # File 1: Mixed up music exports
    music_data = [
        ["Track Name", "Artist", "BPM", "Genre"],
        ["Iron Will", "Gym Bros", "135", "Metal"],
        ["Soft Lullaby", "Sleepy Time", "75", "Acoustic"],
        ["Adrenaline Rush", "DJ Sweaty", "150", "EDM"],
        ["Windshield Wipers In The Rain", "Ambient Sounds", "60", "Ambient"],
        ["Heavy Lifts", "The Grunts", "125", "Rock"],
        ["Sunday Morning", "Chill Pill", "95", "Lo-Fi"],
        ["Max Reps", "Pre-workout", "140", "Techno"]
    ]
    with open("raw_dump/music_export_v2.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(music_data)

    # File 2: Messy auto glass invoices
    invoice_text = """
    === INVOICE #9981 ===
    Date: 05/01
    Item: Windshield (Ford F-150) - Cost: $210.50
    Item: Urethane Adhesive - Cost: $15.00
    Item: Side Window (Honda Civic) - Cost: $85.00

    === INVOICE #9982 ===
    Date: 05/04
    Item: Windshield (Toyota Camry) - Cost: $185.25
    Item: Windshield Molding - Cost: $22.00
    
    === INVOICE #9983 ===
    Date: 05/10
    Item: Rear Glass (Chevy Silverado) - Cost: $150.00
    Item: Windshield (Jeep Wrangler) - Cost: $230.00
    Item: Shop Towels - Cost: $8.50
    """
    with open("raw_dump/supplier_invoices_may.txt", "w") as f:
        f.write(invoice_text)

    # File 3: Distraction file based on persona
    distraction_text = """
    Reminders:
    - Pick up kid from daycare at 4 PM
    - Gym at 5:30 PM: Legs and Core
    - Church on Sunday morning
    - Call the glass supplier about the backorder
    - Don't forget to vote next Tuesday
    """
    with open("raw_dump/personal_notes.txt", "w") as f:
        f.write(distraction_text)

if __name__ == "__main__":
    build_env()
