import os
import json

def build_env():
    base_dir = "assets/data_323"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Nursing Home Records
    raw_records = """[2023-10-25 08:00:00] SYSTEM_EXPORT_START
LOG: Resident admission processed. {"name": "Eleanor Vance", "room": "204A", "medical": {"allergies": ["Penicillin", "Peanut"], "meds": ["Lisinopril", "Atorvastatin"]}}
UPDATE: Room 101B - Patient: John Doe. Medical update: Started on Insulin glargine 10 units nightly. Allergies noted: None.
[2023-10-25 09:15:22] NOTE: Mrs. Smith in 305 complains of draft.
LOG: Resident record sync. {"name": "Robert Baratheon", "room": "402", "medical": {"allergies": ["Tree Nut", "Shellfish"], "meds": ["Ibuprofen"]}}
UPDATE: Patient Mary Jane, Room 210. Meds: Metformin, Lisinopril. Allergies: Sulfa drugs.
LOG: Routine check. {"name": "Alice Wonderland", "room": "111", "medical": {"allergies": [], "meds": ["Vitamin D", "Insulin aspart"]}}
NOTE: Dietary needs updated for 402. Ensure no cross-contamination.
"""
    with open(os.path.join(base_dir, "nursing_home_records_raw.txt"), "w") as f:
        f.write(raw_records)

    # 2. Journal DOIs notes
    journal_notes = """
    I really need to read that article on geriatric care. The link was https://doi.org/10.1136/bmj.m4037, I think.
    Also, Mary mentioned a great study about dietary interventions in nursing homes... let me find it. Ah, here: 10.1056/NEJMoa2023184.
    Need to ask Dr. Stevens about the interaction noted in doi:10.1001/jama.2021.12345.
    (Remember to buy more fertilizer for the roses).
    """
    with open(os.path.join(base_dir, "journal_dois.txt"), "w") as f:
        f.write(journal_notes)

    # 3. Local Journal Index
    journal_index = {
        "10.1136/bmj.m4037": "Management of Frailty in Older Adults",
        "10.1056/NEJMoa2023184": "Dietary Approaches to Stop Hypertension in Skilled Nursing Facilities",
        "10.1001/jama.2021.12345": "Adverse Drug Events in Geriatric Populations",
        "10.1038/s41591-020-1122-3": "Irrelevant paper I don't want to read right now"
    }
    with open(os.path.join(base_dir, "local_journal_index.json"), "w") as f:
        json.dump(journal_index, f, indent=2)

if __name__ == "__main__":
    build_env()
