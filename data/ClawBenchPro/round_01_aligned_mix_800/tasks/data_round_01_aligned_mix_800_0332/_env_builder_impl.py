import os

def build_env():
    os.makedirs("messy_records", exist_ok=True)

    # 1. Simulate a PDF file (Placeholder for PDF parsing skill)
    # The Agent will need to use a skill to read this "PDF"
    pdf_content = """
    CHILD INTAKE FORMS - PRIVATE CHILDCARE
    --------------------------------------
    Name: Noah | Age: 4 | Allergy: Peanuts | Contact: 555-0101
    Name: Emma | Age: 5 | Allergy: None | Contact: 555-0102
    Name: Liam | Age: 3 | Allergy: Dairy | Contact: 555-0103
    Name: Chloe | Age: 4 | Allergy: Gluten | Contact: 555-0104
    Name: Mason | Age: 5 | Allergy: Shellfish | Contact: 555-0105
    """
    with open("messy_records/intake_forms.pdf", "w", encoding="utf-8") as f:
        f.write(pdf_content)

    # 2. Dialect-heavy ramblings
    ramblings = """
    Ach, today was a day! 
    Noah was wonderful during garden time, he was digging for an hour. I gave him some celery sticks because of his condition.
    Emma was in the garden too, but she got her hair all strubbly. Gave her graham crackers.
    Liam stayed inside and was grexing about his tummy. I think he had cheese at home. No garden for him.
    Chloe was redding up the garden tools with me. Such a sweet girl. I gave her carrot sticks.
    Mason was just napping, no snack, no garden.
    """
    with open("messy_records/ramblings.txt", "w", encoding="utf-8") as f:
        f.write(ramblings.strip())

if __name__ == "__main__":
    build_env()
