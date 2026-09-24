import os
import json
import csv
from PIL import Image

def build_env():
    # 移除原本直接可读的 roster.txt
    if os.path.exists("roster.txt"):
        os.remove("roster.txt")

    os.makedirs("records", exist_ok=True)

    # Site A remains JSON
    site_a_data = [
        {"volunteer_name": "Sarah Jenkins", "logged_hours": 4.0},
        {"volunteer_name": "Gary Smith", "logged_hours": 2.0},
        {"volunteer_name": "Chloe Dubois", "logged_hours": 1.5}
    ]
    with open("records/site_a_log.json", "w", encoding="utf-8") as f:
        json.dump(site_a_data, f, indent=4)

    # Site B remains CSV
    with open("records/site_b_log.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Duration"])
        writer.writerow(["Michael Chang", "3.5"])
        writer.writerow(["Emily Davis", "4.0"])
        writer.writerow(["Melissa Vance", "1.5"])

    # Site C becomes a mock scanned image to enforce OCR skill usage
    img_path = "records/site_c_handwritten.png"
    # Create a dummy image representing the scanned handwritten log
    img = Image.new('RGB', (200, 100), color = (255, 255, 255))
    img.save(img_path)

if __name__ == "__main__":
    build_env()
