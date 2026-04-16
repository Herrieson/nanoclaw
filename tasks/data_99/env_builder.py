import os

def build_env():
    base_dir = "assets/data_99"
    records_dir = os.path.join(base_dir, "records_dump")
    os.makedirs(records_dir, exist_ok=True)

    records = [
        """Patient Name: John Doe
Phone: 555-123-4567
ID: PT-8829
Date: 2023-10-01
Diagnosis: Hypertension
Notes: Patient advised to reduce sodium intake.
""",
        """Patient Name: Mary Smith
Phone: 555-987-6543
ID: PT-1023
Date: 2023-10-02
Diagnosis: Type 2 Diabetes
Notes: Discussed insulin management.
""",
        """Patient Name: Robert Johnson
Phone: 555-555-0000
ID: PT-4451
Date: 2023-10-05
Diagnosis: Asthma
Notes: Prescribed new inhaler.
"""
    ]

    for i, rec in enumerate(records):
        file_path = os.path.join(records_dir, f"record_{i}.txt")
        with open(file_path, "w") as f:
            f.write(rec)

if __name__ == "__main__":
    build_env()
