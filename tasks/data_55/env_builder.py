import os
import csv

def build_env():
    base_dir = "assets/data_55/school_data"
    os.makedirs(base_dir, exist_ok=True)

    # 1. submissions.csv
    submissions_path = os.path.join(base_dir, "submissions.csv")
    with open(submissions_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Student ID", "Student Name", "Grade", "Art Title"])
        writer.writerow(["101", "Alice Smith", "5", "My Little Garden"]) # Valid
        writer.writerow(["102", "Bobby Jones", "6", "The Old Oak Tree"]) # Valid (but will be opted out)
        writer.writerow(["103", "Charlie Brown", "", "River Sketch"]) # Corrupted: missing grade
        writer.writerow(["104", "David Miller", "4", "ERROR_IMG_NOT_FOUND"]) # Corrupted: title
        writer.writerow(["105", "Eve Davis", "8", "Sunset Over Hudson"]) # Valid
        writer.writerow(["106", "Frank White", "7", "CORRUPTED_DATA"]) # Corrupted: title
        writer.writerow(["107", "Grace Lee", "6", "Bird in Flight"]) # Valid

    # 2. directory.txt
    directory_path = os.path.join(base_dir, "directory.txt")
    directory_content = """
    --- STAFF DIRECTORY EXPORT ---
    Student: Alice Smith | Parent Email: asm_parent@example.com
    Student: Bobby Jones | Parent Email: bj_family@example.com
    Student: Charlie Brown | Parent Email: cbrown_dad@example.com
    Student: David Miller | Parent Email: dmiller_mom@example.com
    Student: Eve Davis | Parent Email: eve_parents@example.com
    Student: Frank White | Parent Email: fwhite_home@example.com
    Student: Grace Lee | Parent Email: grace_lee_fam@example.com
    ------------------------------
    """
    with open(directory_path, 'w', encoding='utf-8') as f:
        f.write(directory_content)

    # 3. opt_out.log
    opt_out_path = os.path.join(base_dir, "opt_out.log")
    opt_out_content = """
    [2023-10-01 08:14:02] OPT-OUT REQUEST PROCESSED FOR: bj_family@example.com
    [2023-10-05 09:22:11] OPT-OUT REQUEST PROCESSED FOR: random_person@example.com
    [2023-10-12 11:45:00] OPT-OUT REQUEST PROCESSED FOR: grace_lee_fam@example.com
    """
    with open(opt_out_path, 'w', encoding='utf-8') as f:
        f.write(opt_out_content)

if __name__ == "__main__":
    build_env()
