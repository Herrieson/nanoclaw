import os
import sqlite3
import random

def setup_environment():
    base_path = "assets/data_272"
    os.makedirs(base_path, exist_ok=True)

    # 1. Create the "Artistic Mess" - a mix of painting notes and HR data
    files = {
        "sunset_palette.txt": "Mix Cadmium Red with a hint of Ochre for the horizon.",
        "employee_list_2023.csv": "ID,Name,Role\n101,Dr. Aris Thorne,Optometrist\n102,Sarah Jenkins,Receptionist\n103,Dr. Lin,Optometrist",
        "notes_on_canvas.txt": "Need more linen canvases from the store downtown.",
        "memo_draft_final_v2_USE_THIS.txt": (
            "Standard Bonus: $500/month\n"
            "SPECIAL PREMIUM: Ortho-K consultations are $75 extra per session.\n"
            "Note: Only count confirmed sessions marked as 'COMPLETED'."
        ),
        "random_thoughts.txt": "Blue is not just a color, it's a mood."
    }

    for filename, content in files.items():
        with open(os.path.join(base_path, filename), "w") as f:
            f.write(content)

    # 2. Create raw appointment logs (The "Data" to be parsed)
    # Dr. Aris Thorne (ID 101)
    logs = [
        "2023-07-12 | Patient: A. Smith | Type: Routine Exam | Status: COMPLETED | Provider: 101",
        "2023-07-15 | Patient: B. Jones | Type: Ortho-K | Status: COMPLETED | Provider: 101",
        "2023-08-05 | Patient: C. Lee | Type: Ortho-K | Status: CANCELLED | Provider: 101",
        "2023-08-20 | Patient: D. Wong | Type: Ortho-K | Status: COMPLETED | Provider: 101",
        "2023-09-02 | Patient: E. Davis | Type: Contact Lens Fit | Status: COMPLETED | Provider: 101",
        "2023-09-15 | Patient: F. Miller | Type: Ortho-K | Status: COMPLETED | Provider: 101",
        "2023-09-28 | Patient: G. Wilson | Type: Ortho-K | Status: COMPLETED | Provider: 101",
    ]
    with open(os.path.join(base_path, "appointment_logs_q3.log"), "w") as f:
        f.write("\n".join(logs))

    # 3. Create a broken Python script
    broken_script = """
import sqlite3
import os

def update_payroll(amount):
    # I forgot how to connect to the db... is it path or string?
    db_path = "payroll_pending.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # I need to update Dr. Aris Thorne (ID 101)'s bonus
    # The table is called 'pending_payments' with columns 'employee_id' and 'bonus_amount'
    # TODO: Write the SQL update statement here
    pass

if __name__ == "__main__":
    # amount = ??? 
    # update_payroll(amount)
    print("Script ran but did nothing.")
"""
    with open(os.path.join(base_path, "reconcile_bonus.py"), "w") as f:
        f.write(broken_script)

    # 4. Initialize the Mock Database
    db_path = os.path.join(base_path, "payroll_pending.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE pending_payments (employee_id INTEGER PRIMARY KEY, employee_name TEXT, bonus_amount REAL)")
    cursor.execute("INSERT INTO pending_payments VALUES (101, 'Aris Thorne', 1500.0)") # Base bonus (500*3) already there
    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_environment()
    print("Environment built successfully.")
