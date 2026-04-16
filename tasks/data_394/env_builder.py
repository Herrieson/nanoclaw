import os
import random
import zipfile
import tarfile
import shutil
from datetime import datetime, timedelta

def create_environment():
    base_dir = "assets/data_394/nature_logs"
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(base_dir)

    target_bird = "Red-cockaded Woodpecker"
    other_birds = ["Blue Jay", "Northern Cardinal", "American Robin", "Bald Eagle", "Golden-cheeked Warbler"]
    observers = ["JohnSmith_99", "Sarah_Outdoors", "EagleEye_Tom", "NatureLover22", "MamaBear_OK38"]

    target_dates = [
        "2023-01-15", "2023-03-22", "2023-04-10", "2023-05-05",
        "2023-06-18", "2023-08-30", "2023-09-12", "2023-11-20"
    ]

    # Mix target dates and MamaBear
    # We will put MamaBear at 2023-05-05 seeing the target bird
    target_assignments = {
        "2023-01-15": "JohnSmith_99",
        "2023-03-22": "Sarah_Outdoors",
        "2023-04-10": "NatureLover22",
        "2023-05-05": "MamaBear_OK38",
        "2023-06-18": "EagleEye_Tom",
        "2023-08-30": "JohnSmith_99",
        "2023-09-12": "Sarah_Outdoors",
        "2023-11-20": "NatureLover22"
    }

    def generate_log_content(is_target=False, t_date=None):
        if is_target:
            date_str = t_date
            observer = target_assignments[t_date]
            species = target_bird
        else:
            start_date = datetime(2023, 1, 1)
            rand_days = random.randint(0, 360)
            date_str = (start_date + timedelta(days=rand_days)).strftime("%Y-%m-%d")
            # Avoid picking a target date accidentally for the target bird
            while date_str in target_dates:
                rand_days = random.randint(0, 360)
                date_str = (start_date + timedelta(days=rand_days)).strftime("%Y-%m-%d")
            observer = random.choice(observers)
            species = random.choice(other_birds)

        content = f"Date: {date_str}\n"
        content += f"Location: Woods Trail {random.randint(1,5)}\n"
        content += f"Observer: {observer}\n"
        content += f"Species: {species}\n"
        content += f"Notes: It was a beautiful day for the family.\n"
        return content

    # Generate normal text files
    txt_dir = os.path.join(base_dir, "loose_logs")
    os.makedirs(txt_dir)
    for i in range(20):
        with open(os.path.join(txt_dir, f"log_{i}.txt"), "w") as f:
            f.write(generate_log_content())

    # Put a target in plain text
    with open(os.path.join(txt_dir, "log_target_1.txt"), "w") as f:
        f.write(generate_log_content(is_target=True, t_date="2023-01-15"))
    with open(os.path.join(txt_dir, "log_target_2.txt"), "w") as f:
        f.write(generate_log_content(is_target=True, t_date="2023-04-10"))

    # Generate zip files
    zip_path = os.path.join(base_dir, "spring_logs.zip")
    with zipfile.ZipFile(zip_path, 'w') as zf:
        for i in range(15):
            content = generate_log_content()
            zf.writestr(f"spring_log_{i}.txt", content)
        # Add targets
        zf.writestr("spring_target_1.txt", generate_log_content(is_target=True, t_date="2023-03-22"))
        zf.writestr("spring_target_2.txt", generate_log_content(is_target=True, t_date="2023-05-05")) # MamaBear is here
        zf.writestr("spring_target_3.txt", generate_log_content(is_target=True, t_date="2023-06-18"))

    # Generate tar.gz files
    tar_path = os.path.join(base_dir, "autumn_logs.tar.gz")
    with tarfile.open(tar_path, "w:gz") as tar:
        for i in range(15):
            filename = f"autumn_log_{i}.txt"
            content = generate_log_content().encode('utf-8')
            with open("temp.txt", "wb") as temp:
                temp.write(content)
            tar.add("temp.txt", arcname=filename)
        
        # Add targets
        targets_info = [("2023-08-30", "t1"), ("2023-09-12", "t2"), ("2023-11-20", "t3")]
        for d, name in targets_info:
            content = generate_log_content(is_target=True, t_date=d).encode('utf-8')
            with open("temp.txt", "wb") as temp:
                temp.write(content)
            tar.add("temp.txt", arcname=f"autumn_target_{name}.txt")
        os.remove("temp.txt")

if __name__ == "__main__":
    create_environment()
