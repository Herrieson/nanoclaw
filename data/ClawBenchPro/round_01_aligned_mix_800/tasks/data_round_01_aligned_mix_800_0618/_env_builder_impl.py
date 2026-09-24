import os
import csv

def build_env():
    # Create the necessary directories
    os.makedirs("patient_intake", exist_ok=True)
    os.makedirs("nursing_station", exist_ok=True)

    # Mock patient data across different wards
    ward_a_data = [
        ["Patient_Name", "Age", "Primary_Language", "Dietary_Restrictions"],
        ["Maria Garcia", "65", "Spanish", "Diabetic"],
        ["John Smith", "40", "English", "None"],
        ["Betty White", "88", "English", "Soft Foods"]
    ]
    
    ward_b_data = [
        ["Patient_Name", "Age", "Primary_Language", "Dietary_Restrictions"],
        ["Carlos Perez", "50", "Spanish", "Peanut Allergy"],
        ["Jane Doe", "72", "English", "Low Sodium"],
        ["Emily Davis", "35", "English", "None"]
    ]
    
    ward_c_data = [
        ["Patient_Name", "Age", "Primary_Language", "Dietary_Restrictions"],
        ["Luis Rodriguez", "28", "Spanish", "None"],
        ["Tom Wilson", "80", "English", "Gluten Free"],
        ["Rosa Martinez", "45", "Spanish", "None"]
    ]

    # Write the CSV files to the patient_intake directory
    wards = [("ward_A.csv", ward_a_data), ("ward_B.csv", ward_b_data), ("ward_C.csv", ward_c_data)]
    
    for filename, data in wards:
        filepath = os.path.join("patient_intake", filename)
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(data)

if __name__ == "__main__":
    build_env()
