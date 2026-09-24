import sys
import os
import json

def parse_hl7(file_path):
    if not os.path.exists(file_path):
        return json.dumps({"error": f"File not found: {file_path}"})
    
    patients = []
    current_patient = {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                if current_patient and 'Patient_Name' in current_patient:
                    patients.append(current_patient)
                    current_patient = {}
                continue
            
            segments = line.split('|')
            if segments[0] == 'PID':
                # Reconstruct Name from Last^First
                if len(segments) > 5:
                    name_parts = segments[5].split('^')
                    if len(name_parts) >= 2:
                        current_patient['Patient_Name'] = f"{name_parts[1]} {name_parts[0]}"
                # Extract Language
                if len(segments) > 15:
                    lang_code = segments[15]
                    current_patient['Primary_Language'] = "Spanish" if lang_code == "SPA" else "English"
            
            elif segments[0] == 'DG1':
                # Extract Diagnosis
                if len(segments) > 3:
                    current_patient['Diagnosis'] = segments[3]
                    
    if current_patient and 'Patient_Name' in current_patient:
        patients.append(current_patient)
        
    return json.dumps(patients, indent=2)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing file_path argument."}))
    else:
        print(parse_hl7(sys.argv[1]))
