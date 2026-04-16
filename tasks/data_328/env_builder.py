import os
import csv

def build_env():
    base_dir = "assets/data_328"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Create the official schedule
    schedule_path = os.path.join(base_dir, "clinic_schedule.csv")
    schedule_data = [
        ["Date", "Patient_Name", "Service", "Expected_Copay"],
        ["2023-10-15", "Alice Carter", "PT_EVALUATION", "150.00"],
        ["2023-10-15", "David Lee", "PT_FOLLOWUP", "80.00"],
        ["2023-10-16", "Sarah Jenkins", "PT_FOLLOWUP", "80.00"],
        ["2023-10-16", "Michael Vance", "PT_FOLLOWUP", "80.00"],
        ["2023-10-17", "Elena Rostova", "PT_EVALUATION", "150.00"]
    ]
    with open(schedule_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(schedule_data)

    # 2. Create the disorganized desk notes
    notes_path = os.path.join(base_dir, "messy_desk_notes.txt")
    notes_content = """
Ugh, Tuesday, October 15th. My anxiety is through the roof. If I slip a disc demonstrating a deadlift, I'm ruined. No insurance. So stupid of me.
Anyway, Alice Carter came in for her eval. Paid her $150.00 copay in cash. 
David Lee was late, but he paid the $80.00 check for the followup.
I desperately needed to unwind so I went to the art supply store. Picked up some Winsor & Newton Oil Paints for $65.00. The cadmium red is so vibrant, it calms me down. Also grabbed a Large Canvas for $110.00.
Wed Oct 16: Sarah Jenkins, followup. $80.00 paid.
Michael Vance cancelled! No show. That's $80 down the drain. He's on the schedule but didn't pay.
Bought some new Bristle Brushes online, $32.50. Shipping was free at least.
Thursday: Elena Rostova. Tough case, frozen shoulder. Eval done, she paid $150.00 via card.
I need to organize this desk. My hands are shaking from too much coffee.
"""
    with open(notes_path, 'w', encoding='utf-8') as f:
        f.write(notes_content.strip())

if __name__ == "__main__":
    build_env()
