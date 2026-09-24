import os
import csv

def build_env():
    os.makedirs("messy_records", exist_ok=True)

    # File 1: Standard format
    data1 = [
        ["Artwork", "Buyer", "Price", "Date"],
        ["Midnight Tears #1", "Alice L.", "2500", "2023-01-15"],
        ["Crimson Echo", "Bob M.", "1200", "2023-01-20"],
        ["Midnight Tears #4", "Charlie N.", "3000", "2023-02-10"],
    ]
    with open("messy_records/sales_q1.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data1)

    # File 2: Different column names to test data manipulation robustness
    data2 = [
        ["Piece Name", "Acquirer", "Amount", "Sold On"],
        ["Concrete Whisper", "Dave O.", "800", "2023-04-05"],
        ["Midnight Tears #2", "Eve P.", "2500", "2023-05-12"],
        ["Sunlight Illusion", "Frank Q.", "1500", "2023-06-01"],
        ["Midnight Tears #3", "Grace R.", "4500", "2023-06-20"],
    ]
    with open("messy_records/sales_q2.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data2)

    # Noise file
    with open("messy_records/musings.txt", "w") as f:
        f.write("The blue is too harsh today. Reminds me of the ocean, but the ocean is angry. Need more charcoal.\n")
        f.write("Midnight Tears #5 is still unfinished. The tears aren't dark enough.\n")

if __name__ == "__main__":
    build_env()
