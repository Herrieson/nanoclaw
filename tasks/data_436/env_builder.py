import os
import shutil

def build_env():
    base_dir = "assets/data_436/messy_desk"
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(base_dir, exist_ok=True)
    
    file_a = (
        "Classroom observations and formative assessments!\n"
        "John got a 85 on the math quiz.\n"
        "Sarah got 90.\n"
        "Need to soak the lentils overnight for the dal masoor.\n"
    )
    
    file_b = (
        "Authentic Palak Paneer recipe:\n"
        "1. Blanch spinach.\n"
        "2. Fry paneer cubes until golden.\n"
        "3. Mix with ginger, garlic, and garam masala.\n"
        "Serve hot with naan.\n"
    )
    
    file_c = (
        "Student Name,Score,Teacher Notes\n"
        "Alice,78,Needs more scaffolding on fractions\n"
        "Bob,92,Exceeds expectations on the rubric\n"
    )
    
    file_d = (
        "Summative takeaways...\n"
        "Alice scored 82 on the reading test.\n"
        "John scored 88.\n"
        "Sarah achieved 95!\n"
        "Don't forget my yoga mat for the 5 PM class.\n"
    )
    
    with open(os.path.join(base_dir, "notes_monday.txt"), "w") as f:
        f.write(file_a)
    
    with open(os.path.join(base_dir, "dinner_ideas.txt"), "w") as f:
        f.write(file_b)
        
    with open(os.path.join(base_dir, "export_grades.csv"), "w") as f:
        f.write(file_c)
        
    with open(os.path.join(base_dir, "evaluations.log"), "w") as f:
        f.write(file_d)

if __name__ == "__main__":
    build_env()
