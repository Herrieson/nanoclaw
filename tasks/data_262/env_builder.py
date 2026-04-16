import os
import shutil

def build_env():
    base_dir = "assets/data_262"
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(base_dir, exist_ok=True)

    schedule_data = """
# Weekly Schedule Draft
John Doe | 10-24-2023 | 08:00-16:00 [doodle: little stars]
Jane Smith | 2023/10/24 | 09:00-17:00
Alice Johnson | 10-24-2023 | 08:00-12:00 ~drawing a tree~
Mike Lee | 10/25/2023 | 10:00-16:00
John Doe | 2023-10-25 | 08:00-16:00
Jane Smith | 10-25-2023 | 10:00-18:00 [doodle: geometric shapes]
Alice Johnson | 2023/10/25 | 13:00-17:00
"""
    with open(os.path.join(base_dir, "staff_schedule.txt"), "w") as f:
        f.write(schedule_data.strip())

    absences_data = """
[2023-10-24] John Doe - Afternoon doctors appointment. Missed 12:00-16:00.
[2023-10-25] Jane Smith - Late arrival due to traffic. Missed 10:00-11:30.
[2023-10-24] Mike Lee - Call in sick. Whole day. (Note: He wasn't scheduled anyway, just tracking).
"""
    with open(os.path.join(base_dir, "absences.log"), "w") as f:
        f.write(absences_data.strip())

if __name__ == "__main__":
    build_env()
