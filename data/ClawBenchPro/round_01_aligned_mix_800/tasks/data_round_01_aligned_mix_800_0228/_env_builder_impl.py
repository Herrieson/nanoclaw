import os
import csv

def build_env():
    os.makedirs("dock_receipts", exist_ok=True)
    os.makedirs("inventory_reports", exist_ok=True)

    # CSV File - Status removed, replaced with Batch_Code
    with open("dock_receipts/batch_A.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Ingredient", "Batch_Code", "Weight_lbs"])
        writer.writerow(["Shea Butter", "SB-101", "500"])
        writer.writerow(["Lye", "LY-01", "100"])
        writer.writerow(["Lavender Oil", "LO-02", "50"])
        writer.writerow(["Coconut Oil", "CO-44", "200"])
        writer.writerow(["Shea Butter", "SB-102", "150"])

    # TXT downgraded to a dummy PDF scan
    with open("dock_receipts/batch_B_scan.pdf", "wb") as f:
        f.write(b"%PDF-1.4\n%\xE2\xE3\xCF\xD3\n")
        f.write(b"1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n")
        f.write(b"% THIS IS A DUMMY PDF FILE ACTING AS A SCANNED DOCUMENT.\n")

    # Distractor file
    with open("dock_receipts/guest_list.txt", "w") as f:
        f.write("Bat Mitzvah Guest List for Sarah:\n")
        f.write("- Uncle David (Table 5)\n")
        f.write("- Aunt Rachel (Table 5)\n")
        f.write("- The Cohens (Table 3)\n")
        f.write("- Nguyen Family (Table 2) - Need vegetarian options!\n")
        f.write("- 650 napkins ordered.\n")

if __name__ == "__main__":
    build_env()
