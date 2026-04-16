import os
import csv

def create():
    base_dir = "assets/data_231"
    os.makedirs(f"{base_dir}/school_data", exist_ok=True)
    os.makedirs(f"{base_dir}/blog/reviews", exist_ok=True)

    # Roster
    roster_path = f"{base_dir}/school_data/roster.csv"
    with open(roster_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["student_id", "first_name", "last_name", "grade"])
        writer.writerows([
            [101, "John", "Smith", 5],
            [102, "Emma", "Johnson", 5],
            [103, "Miguel", "Garcia", 6],
            [104, "Sophia", "Martinez", 6],
            [105, "Liam", "O'Connor", 5]
        ])

    # Assessment log
    log_path = f"{base_dir}/school_data/assessment_raw.txt"
    with open(log_path, "w") as f:
        f.write("2023-10-01 08:00:00 [ID: 101] Score: 45\n")
        f.write("2023-10-01 08:05:00 [ID: 102] Score: 85\n")
        f.write("2023-10-01 08:10:00 [ID: 101] Score: 55\n") # latest for 101
        f.write("2023-10-01 08:15:00 [ID: 103] Score: 65\n")
        f.write("2023-10-01 08:20:00 [ID: 104] Score: 90\n")

    # Blog posts
    md1 = """# Hamlet Review

<script>alert('xss');</script>
<span class="redacted">CENSORED</span> truly captured the essence of hesitation.
"""
    md2 = """# Romeo and Juliet

A classic by <span class="redacted">CENSORED</span>. 
<script src="http://evil.com/mal.js"></script>
Tragic and beautiful.
"""
    with open(f"{base_dir}/blog/reviews/hamlet.md", "w") as f:
        f.write(md1)
    with open(f"{base_dir}/blog/reviews/romeo.md", "w") as f:
        f.write(md2)

if __name__ == "__main__":
    create()
