import os
import csv

def build_env():
    os.makedirs("messy_records", exist_ok=True)

    csv_data = [
        ["Child_Name", "Age", "Known_Allergies", "Emergency_Contact"],
        ["Noah", "4", "Peanuts", "555-0101"],
        ["Emma", "5", "None", "555-0102"],
        ["Liam", "3", "Dairy", "555-0103"],
        ["Chloe", "4", "Gluten", "555-0104"],
        ["Mason", "5", "Shellfish", "555-0105"]
    ]
    
    with open("messy_records/intake.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

    ramblings = """
    Oh my, I am so ferhuddled today. My heart is just racing thinking about the parents' meeting tomorrow. I hope I didn't forget anything.
    Noah loved garden time today, he was digging in the dirt for an hour! Since he can't have his usual, we gave him celery sticks as a safe snack.
    Emma was in the garden too, but she got her hair all strubbly and muddy. Gave her some graham crackers.
    Liam stayed inside and read books. He was grexing about his tummy, probably because he accidentally had a tiny bit of cheese at home yesterday - gotta watch that dairy! I gave him apples later.
    Chloe was redding up the garden tools with me. Such a sweet girl, always helping. She loves carrot sticks for her safe snack.
    Mason was just napping all afternoon, bless his heart. Didn't even want a snack.
    """
    
    with open("messy_records/ramblings.txt", "w", encoding="utf-8") as f:
        f.write(ramblings.strip())

if __name__ == "__main__":
    build_env()
