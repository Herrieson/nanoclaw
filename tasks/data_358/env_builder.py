import os
import shutil

def build_env():
    base_dir = "assets/data_358"
    raw_data_dir = os.path.join(base_dir, "raw_data")
    
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(raw_data_dir)

    # Generate bilingual raw data files
    data = [
        {"file": "resp_01.txt", "content": "Name: John Doe\nEmail: jdoe@school.edu\nInterest Score: 9\nComments: Let's save the turtles!"},
        {"file": "resp_02.txt", "content": "Nombre: Maria Garcia\nCorreo: maria.g@gmail.com\nPuntaje: 8\nComentarios: Muy importante."},
        {"file": "resp_03.txt", "content": "Name: Alex Smith\nEmail: alexxx@yahoo.com\nInterest Score: 5\nComments: Meh."},
        {"file": "resp_04.txt", "content": "Nombre: Carlos Ruiz\nCorreo: cruiz99@hotmail.com\nPuntaje: 10\nComentarios: ¡Quiero ayudar!"},
        {"file": "resp_05.txt", "content": "Name: Sarah Connor\nEmail: sarah.c@school.edu\nInterest Score: 7\nComments: Busy with sports mostly."},
        {"file": "resp_06.txt", "content": "Nombre: Lucia Fernandez\nCorreo: luciaf@gmail.com\nPuntaje: 3\nComentarios: No tengo tiempo."},
    ]

    for d in data:
        with open(os.path.join(raw_data_dir, d["file"]), "w", encoding="utf-8") as f:
            f.write(d["content"])

    # Generate the broken script
    broken_script = """import os
import csv

# I think this is where my files are?
data_dir = "my_desktop/survey_data" 
output_file = "members.csv"

good_people = []

for filename in os.listdir(data_dir):
    with open(data_dir + "/" + filename, "r") as f:
        lines = f.readlines()
        name = ""
        email = ""
        score = 0
        for line in lines:
            if line.startswith("Name:"):
                name = line.split(":")[1].strip()
            if line.startswith("Email:"):
                email = line.split(":")[1].strip()
            if line.startswith("Interest Score:"):
                score = line.split(":")[1].strip()

        # Only get people who scored 8, 9, or 10
        if score >= 8:
            good_people.append([name, email])

with open(output_file, "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["Name", "Email"])
    writer.writerows(good_people)
"""

    with open(os.path.join(base_dir, "process.py"), "w", encoding="utf-8") as f:
        f.write(broken_script)

if __name__ == "__main__":
    build_env()
