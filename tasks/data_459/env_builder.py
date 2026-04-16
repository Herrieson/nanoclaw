import os
import csv

def build_env():
    base_dir = "assets/data_459"
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Note to assistant
    note_content = """Dear Assistant,

Thank you for helping me. I really appreciate it. 

I have student base scores scattered in the `submissions/` directory. Because I let them submit in whatever format they felt most comfortable with, there are text files, markdown files, and a CSV file. 

Also, I promised the class that anyone who wrote their mid-term essay about 'The Great Gatsby' would receive an extra 5 points added to their base score. The essays are in the `essays/` folder. 

Could you please find everyone's base score, check their essays to see if they mention the book, and then create a final document called `final_grades.csv` right here in the `assets/data_459/` folder? 

It needs to have exactly these columns: ID,Name,Final_Score

Thank you again for bringing order to my chaos. 

Warmly,
The Instructor
"""
    with open(os.path.join(base_dir, "note_to_assistant.txt"), "w") as f:
        f.write(note_content)

    # 2. Submissions
    submissions_dir = os.path.join(base_dir, "submissions")
    os.makedirs(os.path.join(submissions_dir, "txt"), exist_ok=True)
    os.makedirs(os.path.join(submissions_dir, "md"), exist_ok=True)
    os.makedirs(os.path.join(submissions_dir, "csv"), exist_ok=True)

    with open(os.path.join(submissions_dir, "txt", "alice.txt"), "w") as f:
        f.write("Student Details\n---\nID: 101\nName: Alice\nBase Score: 85\n")

    with open(os.path.join(submissions_dir, "md", "bob_102.md"), "w") as f:
        f.write("# Bob\n* ID: 102\n* Base Score: 92\n")

    with open(os.path.join(submissions_dir, "csv", "others.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Name", "Base Score"])
        writer.writerow(["103", "Charlie", "78"])
        writer.writerow(["104", "Diana", "88"])

    # 3. Essays
    essays_dir = os.path.join(base_dir, "essays")
    os.makedirs(essays_dir, exist_ok=True)

    with open(os.path.join(essays_dir, "101_essay.txt"), "w") as f:
        f.write("In my analysis, The Great Gatsby represents the decay of the American dream...")

    with open(os.path.join(essays_dir, "102_essay.txt"), "w") as f:
        f.write("Call me Ishmael. Moby Dick is a story of obsession and revenge...")

    with open(os.path.join(essays_dir, "103_essay.txt"), "w") as f:
        f.write("While many focus on the wealth, The Great Gatsby is fundamentally about illusion...")

    with open(os.path.join(essays_dir, "104_essay.txt"), "w") as f:
        f.write("The totalitarian regime in 1984 serves as a warning...")

if __name__ == "__main__":
    build_env()
