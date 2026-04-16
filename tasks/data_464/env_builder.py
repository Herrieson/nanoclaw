import os

def build_env():
    base_dir = "assets/data_464"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Create the messy POS log file
    raw_log_content = """
SYS_INIT: 2023-10-01 08:00:00
WARN: Scanner offline at terminal 2.
2023-10-01|Dune;Frank Herbert|Sci-Fi||15.99||2
2023-10-01|The Hobbit;J.R.R. Tolkien|Fantasy||10.00||3
2023-10-02|Foundation;Isaac Asimov|Sci-Fi||12.50||1
ERROR: DB Connection timeout. Retrying...
2023-10-02|To Kill a Mockingbird;Harper Lee|Fiction||9.99||1
2023-10-03|Neuromancer;William Gibson|Sci-Fi||14.00||2
2023-10-03|Dune;Frank Herbert|Sci-Fi||15.99||1
2023-10-04|1984;George Orwell|Dystopian||11.50||4
2023-10-05|Left Hand of Darkness;Ursula K. Le Guin|Sci-Fi||16.50||1
2023-10-05|Mistborn;Brandon Sanderson|Fantasy||20.00||2
2023-10-06|The Way of Kings;Brandon Sanderson|Fantasy||25.00||1
CORRUPTION_DETECTED_AT_BYTE_0x4F2A
2023-10-07|Foundation;Isaac Asimov|Sci-Fi||12.50||2
2023-10-07|Good Omens;Neil Gaiman|Fantasy||18.00||1
    """.strip()

    with open(os.path.join(base_dir, "raw_sales_export.log"), "w", encoding="utf-8") as f:
        f.write(raw_log_content)

    # 2. Create the Hugo winners list
    hugo_winners_content = """
Frank Herbert
Isaac Asimov
William Gibson
Ursula K. Le Guin
Neil Gaiman
Arthur C. Clarke
Philip K. Dick
    """.strip()

    with open(os.path.join(base_dir, "hugo_winners.txt"), "w", encoding="utf-8") as f:
        f.write(hugo_winners_content)

if __name__ == "__main__":
    build_env()
