import os
import csv
import json
import random
from xml.etree.ElementTree import Element, SubElement, tostring

def build_env():
    random.seed(42)

    # Base directories
    dirs = [
        "raw_dump/devices/phone",
        "raw_dump/devices/laptop",
        "raw_dump/devices/tablet",
        "raw_dump/devices/corrupted",
        "raw_dump/manuals",
        "raw_dump/invoices/branch_north",
        "raw_dump/invoices/branch_south",
        "raw_dump/invoices/recycle_bin",
        "raw_dump/catalog"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 1. Multi-hop Clue: Energy Code Manual
    energy_map = {
        "E_SLEEP": 60,
        "E_CHILL": 90,
        "E_WARMUP": 115,
        "E_CARDIO": 130,
        "E_LIFT": 145,
        "E_MAX": 160
    }
    with open("raw_dump/manuals/energy_map.json", "w") as f:
        json.dump(energy_map, f, indent=4)

    # 2. Fragmented Music Data Generation
    def generate_music_data(device, num_files, tracks_per_file):
        for i in range(num_files):
            tracks = []
            for j in range(tracks_per_file):
                bpm = random.randint(70, 170)
                energy = random.choice(list(energy_map.keys()))
                track_name = f"Track_{device}_{i}_{j}"
                tracks.append({"title": track_name, "artist": f"Artist_{j}", "bpm": bpm, "energy": energy})
            
            # Decoy/Corrupted injections
            if i % 5 == 0:
                with open(f"raw_dump/devices/corrupted/bad_{device}_{i}.json", "w") as f:
                    json.dump([{"title": f"CORRUPTED_{device}_{i}", "bpm": 999}], f)

            # File Format Heterogeneity
            if device == "phone":
                with open(f"raw_dump/devices/phone/export_{i}.json", "w") as f:
                    json.dump({"tracks": [{"title": t["title"], "artist": t["artist"], "bpm": t["bpm"]} for t in tracks]}, f)
            elif device == "laptop":
                with open(f"raw_dump/devices/laptop/export_{i}.csv", "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Title", "Artist", "EnergyCode"])
                    for t in tracks:
                        writer.writerow([t["title"], t["artist"], t["energy"]])
            elif device == "tablet":
                root = Element("playlist")
                for t in tracks:
                    track_el = SubElement(root, "track")
                    SubElement(track_el, "title").text = t["title"]
                    SubElement(track_el, "artist").text = t["artist"]
                    SubElement(track_el, "bpm").text = str(t["bpm"])
                with open(f"raw_dump/devices/tablet/export_{i}.xml", "w") as f:
                    f.write(tostring(root, encoding="unicode"))

    generate_music_data("phone", 20, 15)
    generate_music_data("laptop", 20, 15)
    generate_music_data("tablet", 20, 15)

    # 3. Multi-hop Clue: Parts Catalog Generation
    parts = []
    # Valid targets: Windshields
    for i in range(1, 16):
        parts.append({"part_no": f"GLS-WND-{i:03d}", "desc": f"Windshield Model {i}", "price": round(random.uniform(150.0, 400.0), 2)})
    # Decoys: Side glass, accessories, chemicals
    for i in range(1, 11):
        parts.append({"part_no": f"GLS-SID-{i:03d}", "desc": f"Side Glass Model {i}", "price": round(random.uniform(50.0, 100.0), 2)})
    for i in range(1, 21):
        parts.append({"part_no": f"ACC-{i:03d}", "desc": f"Wiper/Accessory {i}", "price": round(random.uniform(5.0, 30.0), 2)})
    for i in range(1, 11):
        parts.append({"part_no": f"CHM-{i:03d}", "desc": f"Urethane Adhesive {i}", "price": round(random.uniform(10.0, 25.0), 2)})

    with open("raw_dump/catalog/parts_index.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["part_no", "description", "unit_price"])
        for p in parts:
            writer.writerow([p["part_no"], p["desc"], f"{p['price']:.2f}"])

    # 4. Fragmented Invoice Data Generation
    statuses = ["PAID", "COMPLETED", "VOID", "CANCELLED", "PENDING"]
    
    # Branch North: Unstructured Text Parsing
    for i in range(1, 51):
        status = random.choice(statuses)
        lines = []
        lines.append(f"=== INVOICE #{1000+i} ===")
        lines.append(f"STATUS: {status}")
        lines.append("Date: 2023-10-05")
        
        num_items = random.randint(1, 5)
        selected_parts = random.sample(parts, num_items)
        for p in selected_parts:
            qty = random.randint(1, 3)
            lines.append(f"Item: {p['part_no']} ({p['desc']}) - Qty: {qty} - Unit Price: ${p['price']:.2f}")
        
        with open(f"raw_dump/invoices/branch_north/inv_{1000+i}.txt", "w") as f:
            f.write("\n".join(lines))

        # Noise: Decoy invoices in recycle_bin
        if i % 10 == 0:
            with open(f"raw_dump/invoices/recycle_bin/inv_{1000+i}_old.txt", "w") as f:
                f.write("\n".join(lines).replace(status, "PAID")) 

    # Branch South: Missing Price Info (Requires Join)
    for i in range(1, 51):
        status = random.choice(statuses)
        num_items = random.randint(1, 5)
        selected_parts = random.sample(parts, num_items)
        
        items = [{"part_no": p["part_no"], "qty": random.randint(1, 3)} for p in selected_parts]
        inv = {
            "invoice_no": f"S-{2000+i}",
            "status": status,
            "date": "2023-10-06",
            "items": items
        }
        with open(f"raw_dump/invoices/branch_south/inv_S_{2000+i}.json", "w") as f:
            json.dump(inv, f, indent=4)

if __name__ == "__main__":
    build_env()
