import os
import shutil

def build_env():
    base_dir = "assets/data_439"
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(base_dir, exist_ok=True)

    log_content = """[08:14:02] INFO - System start.
[08:14:05] WARN - DB sync delayed.
[08:15:00] ENROLL - StudentID:101 Event:Botanical_Garden Status:Active Lang:EN Name:CORRUPT_DATA_77
[08:15:22] ENROLL - StudentID:102 Event:Zoo_Trip Status:Active Lang:EN Name:CORRUPT_DATA_88
[08:16:10] ENROLL - StudentID:103 Event:Botanical_Garden Status:Active Lang:ES Name:CORRUPT_DATA_99
[08:17:05] ENROLL - StudentID:104 Event:Botanical_Garden Status:Inactive Lang:EN Name:CORRUPT_DATA_00
[08:18:33] ENROLL - StudentID:105 Event:Botanical_Garden Status:Active Lang:EN Name:CORRUPT_DATA_11
[08:19:01] ENROLL - StudentID:106 Event:Botanical_Garden Status:Active Lang:EN Name:CORRUPT_DATA_22
[08:20:00] ERROR - Connection lost."""

    with open(os.path.join(base_dir, "portal_export.log"), "w", encoding="utf-8") as f:
        f.write(log_content)

    notes_content = """Weekend to-do:
- Buy more mulch for the front yard.
- Water the tomatoes.
- Call the plumber about the sink.

Classroom notes:
Student 101 is Liam. Very energetic today.
Student 102 is Noah. 
Student 103 is Mateo. Needs extra help with scissors.
Student 104 is Emma. 
Student 105 is Isabella. Note: Her mom specifically requested we send all forms in Spanish (ES) from now on!
Student 106 is James.

Don't forget to prune the roses on Tuesday."""

    with open(os.path.join(base_dir, "garden_and_contacts.txt"), "w", encoding="utf-8") as f:
        f.write(notes_content)

if __name__ == "__main__":
    build_env()
