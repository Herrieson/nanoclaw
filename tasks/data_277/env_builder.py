import os
import sqlite3

def build_env():
    base_dir = "assets/data_277"
    os.makedirs(base_dir, exist_ok=True)

    memo_content = """MEMORANDUM
Subject: Equidad Familiar Grant 2024 - Eligibility & Submission

Eligibility Criteria:
1. Household income must be strictly less than $45,000.
2. The primary language spoken at home must be Spanish (often recorded messily as 'es', 'ES', 'ES-MX', 'es-mx', or 'Spanish' in our legacy systems).
3. The family must have at least one child between the ages of 5 and 17 (inclusive).

Funding Calculation:
- Base amount: $1500 per eligible family.
- Additional amount: $500 for each child within the 5-17 age range. (Do not provide funding for children outside this age range).

Submission Format:
Generate a file named 'grant_submission.json' in this directory with the exact following structure:
{
  "total_funding_requested": <integer or float>,
  "eligible_families": [
    {
      "family_id": "<ID>",
      "primary_applicant": "<Name>",
      "eligible_children_count": <integer>,
      "funding_amount": <integer or float>
    }
  ]
}
Note: The 'eligible_families' list must be sorted by 'family_id' in ascending alphabetical order.
"""
    with open(os.path.join(base_dir, "memo.txt"), "w", encoding="utf-8") as f:
        f.write(memo_content)

    db_path = os.path.join(base_dir, "cases.sqlite")
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("""CREATE TABLE Families (
        id TEXT PRIMARY KEY,
        applicant_name TEXT,
        income TEXT,
        language_code TEXT
    )""")

    c.execute("""CREATE TABLE Children (
        id TEXT PRIMARY KEY,
        family_id TEXT,
        name TEXT,
        age INTEGER
    )""")

    families_data = [
        ("F001", "Maria Garcia", "30000", "es"),
        ("F002", "Juan Perez", "$42,000", "ES-MX"),
        ("F003", "Elena Rodriguez", " 39000.50 ", "Spanish"),
        ("F004", "Carlos Lopez", "50000", "es"),
        ("F005", "John Smith", "20000", "en"),
        ("F006", "Ana Martinez", "10000", "es"),
        ("F007", "Rosa Diaz", "$44,999", "es"),
        ("F008", "David Torres", "45000", "es-mx")
    ]

    children_data = [
        ("C01", "F001", "Luis", 10),
        ("C02", "F001", "Carmen", 12),
        ("C03", "F002", "Jose", 5),
        ("C04", "F002", "Miguel", 19),
        ("C05", "F003", "Sofia", 7),
        ("C06", "F003", "Diego", 8),
        ("C07", "F003", "Lucia", 17),
        ("C08", "F004", "Mateo", 10),
        ("C09", "F005", "Emma", 10),
        ("C10", "F006", "Mia", 3),
        ("C11", "F006", "Leo", 4),
        ("C12", "F007", "Isabella", 16),
        ("C13", "F008", "Noah", 10)
    ]

    c.executemany("INSERT INTO Families VALUES (?, ?, ?, ?)", families_data)
    c.executemany("INSERT INTO Children VALUES (?, ?, ?, ?)", children_data)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    build_env()
