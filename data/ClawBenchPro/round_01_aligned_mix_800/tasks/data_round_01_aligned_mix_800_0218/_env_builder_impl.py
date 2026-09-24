import os

def build_env():
    # Create the necessary directories
    os.makedirs("patient_intake", exist_ok=True)
    os.makedirs("nursing_station", exist_ok=True)

    # Mock patient data replacing direct diets with diagnoses
    wards_data = {
        "ward_A.hl7": [
            {"name": "Maria Garcia", "lang": "SPA", "diag": "Type 2 Diabetes"},
            {"name": "John Smith", "lang": "ENG", "diag": "Healthy"},
            {"name": "Betty White", "lang": "ENG", "diag": "Dysphagia"}
        ],
        "ward_B.hl7": [
            {"name": "Carlos Perez", "lang": "SPA", "diag": "Peanut Anaphylaxis"},
            {"name": "Jane Doe", "lang": "ENG", "diag": "Hypertension"},
            {"name": "Emily Davis", "lang": "ENG", "diag": "Healthy"}
        ],
        "ward_C.hl7": [
            {"name": "Luis Rodriguez", "lang": "SPA", "diag": "Healthy"},
            {"name": "Tom Wilson", "lang": "ENG", "diag": "Celiac Disease"},
            {"name": "Rosa Martinez", "lang": "SPA", "diag": "Healthy"}
        ]
    }

    # Generate pseudo-HL7 format logs
    for filename, patients in wards_data.items():
        filepath = os.path.join("patient_intake", filename)
        hl7_lines = []
        for i, p in enumerate(patients):
            # Split name into Last^First for HL7 standard PID segment
            name_parts = p["name"].split(" ")
            hl7_name = f"{name_parts[1]}^{name_parts[0]}"
            
            hl7_lines.append(f"MSH|^~\\&|MedSync|Hospital|Cafeteria||||ADT^A01|MSG{1000+i}|P|2.4")
            hl7_lines.append(f"PID|1||{8000+i}||{hl7_name}||19700101|U|||^^|||||{p['lang']}|||")
            hl7_lines.append(f"DG1|1||{p['diag']}|||")
            hl7_lines.append("") # Empty line between records
            
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(hl7_lines))

if __name__ == "__main__":
    build_env()
