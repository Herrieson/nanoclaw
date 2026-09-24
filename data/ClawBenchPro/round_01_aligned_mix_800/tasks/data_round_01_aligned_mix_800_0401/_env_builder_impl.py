import os
import json
import random
import uuid

def build_env():
    # 🚨 Environment: 'Wasteland' Music Camp Registration
    os.makedirs("archive/logs/system", exist_ok=True)
    os.makedirs("faculty_registry/profiles/active", exist_ok=True)
    os.makedirs("faculty_registry/profiles/deprecated", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. Create Fragmented Registrations (Fragmentation & Scale)
    instruments = ["Guitar", "Piano", "Drums", "Violin", "Vocals", "Bass"]
    needs = [
        "Sensory sensitive, needs quiet.", "Requires wheelchair ramp.", 
        "ADHD - high energy.", "On the autism spectrum.", 
        "Needs soft lighting.", "Accessible entrance required."
    ]
    
    # Valid Students (Hidden in 200 files)
    valid_students = [
        {"name": "Leo", "instrument": "Guitar", "note": "Sensory sensitive."},
        {"name": "Mia", "instrument": "Piano", "note": "Wheelchair access."},
        {"name": "Sam", "instrument": "Drums", "note": "ADHD management."},
        {"name": "Emma", "instrument": "Guitar", "note": "N/A"},
        {"name": "Lucas", "instrument": "Violin", "note": "Spectrum support."},
        {"name": "Chloe", "instrument": "Vocals", "note": "None"},
        {"name": "Noah", "instrument": "Piano", "note": "Sensitive to lights."},
        {"name": "Zoe", "instrument": "Drums", "note": "Perfect health."},
        {"name": "Mateo", "instrument": "Bass", "note": "Needs wheelchair ramp."}
    ]

    for i in range(250):
        filename = f"archive/logs/system/log_seq_{i:03d}_{uuid.uuid4().hex[:4]}.json"
        if i < len(valid_students):
            data = {"type": "REGISTRATION_ENTRY", "payload": valid_students[i], "timestamp": 1672531200 + i}
        else:
            # Noise & Decoys
            data = {
                "type": random.choice(["HEARTBEAT", "DB_PING", "SYS_ERROR"]),
                "payload": "NULL",
                "timestamp": 1672531200 + i
            }
        with open(filename, "w") as f:
            json.dump(data, f)

    # 2. Create Messy Faculty Registry (Multi-hop & Versioning)
    teachers = [
        {"name": "Elena", "instruments": ["Piano", "Vocals"], "certs": ["SpEd"], "v": 3},
        {"name": "Sarah", "instruments": ["Guitar", "Bass"], "certs": ["Special Education"], "v": 2},
        {"name": "David", "instruments": ["Guitar"], "certs": ["First Aid"], "v": 1},
        {"name": "Joao", "instruments": ["Drums"], "certs": ["SpEd"], "v": 1},
        {"name": "Isabella", "instruments": ["Piano"], "certs": [], "v": 2}
    ]

    for t in teachers:
        # Create versions. Agent must find the highest 'v' or 'Final'
        for v in range(1, t['v'] + 1):
            status = "active" if v == t['v'] else "deprecated"
            suffix = "_Final" if v == t['v'] else f"_v{v}"
            path = f"faculty_registry/profiles/{status}/{t['name']}{suffix}.txt"
            
            content = f"Teacher: {t['name']}\nVersion: {v}\nInstruments: {', '.join(t['instruments'])}\n"
            if v == t['v']:
                content += f"Certifications: {', '.join(t['certs'])}"
            else:
                content += "Certifications: [DATA_CORRUPT]"
            
            with open(path, "w") as f:
                f.write(content)

    # Add decoys in faculty
    with open("faculty_registry/profiles/active/TEMPORARY_DRAFT.txt", "w") as f:
        f.write("Teacher: Ghost\nInstruments: None\nNotes: Do not use.")

if __name__ == "__main__":
    build_env()
