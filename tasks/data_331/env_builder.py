import os
import random
import json

def build_env():
    # Base directory
    base_dir = "assets/data_331"
    os.makedirs(base_dir, exist_ok=True)
    
    dump_path = os.path.join(base_dir, "clinic_records_dump.txt")
    
    # We will mix JSON lines, CSV lines, and weird pipe-separated lines
    # Toxic brand: "NatureScraps Premium"
    # Safe brands: "HappyKibble", "VetChoice", "PurrDiet"
    
    records = [
        # Toxic cases (GI issues)
        {"type": "json", "data": {"patient": "Bella", "species": "Dog", "owner": "Sarah Jenkins", "phone": "555-0101", "diet": "NatureScraps Premium", "symptoms": "Severe vomiting and diarrhea since Tuesday."}},
        {"type": "csv", "data": "Max,Dog,Mark Thompson,555-0102,NatureScraps Premium,Lethargy and GI tract inflammation"},
        {"type": "pipe", "data": "Luna|Cat|Emily Davis|555-0103|NatureScraps Premium|Constant vomiting, unable to hold down water"},
        {"type": "json", "data": {"patient": "Charlie", "species": "Dog", "owner": "Robert Wilson", "phone": "555-0104", "diet": "NatureScraps Premium", "symptoms": "Bloody diarrhea, stomach pain."}},
        {"type": "csv", "data": "Daisy,Dog,Jessica Martinez,555-0105,NatureScraps Premium,Stomach distension and vomiting"},
        
        # Safe cases (Other issues or safe brands)
        {"type": "json", "data": {"patient": "Milo", "species": "Cat", "owner": "John Smith", "phone": "555-0201", "diet": "HappyKibble", "symptoms": "Annual rabies vaccination."}},
        {"type": "csv", "data": "Buddy,Dog,Michael Brown,555-0202,VetChoice,Limping on left hind leg. Possible sprain."},
        {"type": "pipe", "data": "Chloe|Cat|Ashley Taylor|555-0203|PurrDiet|Ear mites and scratching"},
        {"type": "json", "data": {"patient": "Rocky", "species": "Dog", "owner": "David Anderson", "phone": "555-0204", "diet": "HappyKibble", "symptoms": "Hot spots on tail."}},
        {"type": "csv", "data": "Zoe,Dog,Amanda Thomas,555-0205,VetChoice,Routine dental cleaning"},
        {"type": "pipe", "data": "Leo|Cat|James Jackson|555-0206|HappyKibble|Swallowed a toy mouse, requires surgery"},
        
        # An owner with NatureScraps but maybe here for something else (should still be warned)
        {"type": "json", "data": {"patient": "Sadie", "species": "Dog", "owner": "Christopher White", "phone": "555-0106", "diet": "NatureScraps Premium", "symptoms": "Checkup for mild lethargy, owner states stomach feels tight."}}
    ]
    
    # Shuffle records to make it chaotic
    random.seed(42)
    random.shuffle(records)
    
    with open(dump_path, "w", encoding="utf-8") as f:
        f.write("=== CLINIC EXPORT v2.1 ===\n")
        f.write("WARN: System error during export. Formats may vary.\n\n")
        for r in records:
            if r["type"] == "json":
                f.write(json.dumps(r["data"]) + "\n")
            elif r["type"] == "csv":
                f.write(r["data"] + "\n")
            elif r["type"] == "pipe":
                f.write(r["data"] + "\n")
            # add some noise
            if random.random() > 0.7:
                f.write("DEBUG: Transaction timeout...\n")

if __name__ == "__main__":
    build_env()
