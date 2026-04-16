import os
import csv
import json

def build_env():
    base_dir = "assets/data_463"
    case_dir = os.path.join(base_dir, "case_files")
    
    # Create directories
    os.makedirs(case_dir, exist_ok=True)
    
    # Generate schedule.csv
    schedule_data = [
        ["Case ID", "Patient Name", "Age", "Appointment Status", "Guardian Contact"],
        ["CW-101", "Emma Watson", "8", "Missed", "555-0101"],      # Target
        ["CW-102", "Liam Smith", "14", "Missed", "555-0102"],      # Over 12
        ["CW-103", "Olivia Davis", "5", "Attended", "555-0103"],   # Attended
        ["CW-104", "Noah Garcia", "10", "Missed", "555-0104"],     # No keywords
        ["CW-105", "Sophia Martinez", "7", "Missed", "555-0105"],  # Target
        ["CW-106", "Jackson Lee", "11", "Missed", "555-0106"],     # Target
        ["CW-107", "Isabella Brown", "9", "Attended", "555-0107"], # Attended
    ]
    
    with open(os.path.join(case_dir, "schedule.csv"), "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(schedule_data)
        
    # Generate messy notes
    notes = {
        "notes_CW-101.txt": "Emma's mother mentioned they might be evicted soon. High risk of housing instability. Need to follow up with local shelters.",
        "liam_case_102_notes.md": "Liam is doing okay in school but they are dealing with severe food insecurity at home. (Note: He missed his appt!)",
        "olivia_update.txt": "Olivia came in today. Very bright girl. We discussed housing instability in the neighborhood, but her family is secure.",
        "CW-104_draft.txt": "Noah missed his appointment. Left a voicemail. No immediate concerns noted during last visit.",
        "sophia_m.txt": "Family is struggling financially. Mother reported food insecurity and asked about food banks.",
        "jackson_106.txt": "Jackson's foster parents called. They are facing housing instability due to lease issues. He missed Tuesday's session.",
        "book_club_notes.txt": "The novel was so beautifully written. The themes of food insecurity in the 1920s were haunting. Need to return book to library.",
        "volunteer_roster.txt": "Sunday church duties: 9AM setup, 11AM greeting. Don't forget to bring the cookies."
    }
    
    for filename, content in notes.items():
        with open(os.path.join(case_dir, filename), "w") as f:
            f.write(content)

if __name__ == "__main__":
    build_env()
