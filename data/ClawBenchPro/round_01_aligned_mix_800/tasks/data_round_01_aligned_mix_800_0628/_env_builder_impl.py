import os
import csv

def build_env():
    os.makedirs("dock_receipts", exist_ok=True)
    os.makedirs("inventory_reports", exist_ok=True)

    with open("dock_receipts/batch_A.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Ingredient", "Status", "Weight_lbs"])
        writer.writerow(["Shea Butter", "Certified Organic", "500"])
        writer.writerow(["Lye", "Pending", "100"])
        writer.writerow(["Lavender Oil", "Certified Organic", "50"])
        writer.writerow(["Coconut Oil", "Rejected", "200"])
        writer.writerow(["Shea Butter", "Certified Organic", "150"])

    with open("dock_receipts/batch_B.txt", "w") as f:
        f.write("Messy Log from Tuesday\n")
        f.write("----------------------\n")
        f.write("Item: Rose Water | Cert: Certified Organic | Wt: 30 lbs\n")
        f.write("Item: Artificial Dye | Cert: Rejected | Wt: 500 lbs\n")
        f.write("Item: Lavender Oil | Cert: Pending | Wt: 10 lbs\n")

    with open("dock_receipts/guest_list.txt", "w") as f:
        f.write("Bat Mitzvah Guest List for Sarah:\n")
        f.write("- Uncle David (Table 5)\n")
        f.write("- Aunt Rachel (Table 5)\n")
        f.write("- The Cohens (Table 3)\n")
        f.write("- Nguyen Family (Table 2) - Need vegetarian options!\n")
        f.write("- 650 napkins ordered.\n")

if __name__ == "__main__":
    build_env()
