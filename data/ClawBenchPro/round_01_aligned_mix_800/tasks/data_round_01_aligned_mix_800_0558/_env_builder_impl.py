import os
import json
import random
import uuid
from datetime import datetime, timedelta

def build_env():
    # 1. Create Directories
    os.makedirs("deliverables", exist_ok=True)
    os.makedirs("admin_docs", exist_ok=True)
    
    # 2. Generate Admin Docs (Decoys & Clues)
    project_registry = {
        "projects": [
            {"name": "Downtown Residential Complex", "project_code": "PROJ-101-RES", "status": "active"},
            {"name": "Highway 9 Overpass Repair", "project_code": "PROJ-550-HWY", "status": "completed"},
            {"name": "New Municipal Build", "project_code": "PROJ-77X-MUNI", "status": "active"},
            {"name": "Southside Shopping Mall", "project_code": "PROJ-999-COM", "status": "on_hold"}
        ]
    }
    with open("admin_docs/project_master_registry.json", "w") as f:
        json.dump(project_registry, f, indent=4)
        
    with open("admin_docs/OSHA_compliance_memo.txt", "w") as f:
        f.write("""MEMORANDUM - CITY INSPECTOR OFFICE
To: All Site Managers
Subject: Automated Transcription Tagging & Safety Report Filtering

We are aware that the new cloud dictation software automatically appends a [SAFETY_VIOLATION] tag whenever the keyword algorithms detect words like "hazard", "danger", or "issue".

However, Site Managers MUST manually filter these before submitting the official report. 
According to City OSHA rules, a valid construction hazard ONLY involves:
- Structural integrity (e.g., scaffolding, trenches, framing)
- Electrical hazards (e.g., exposed wiring, grid issues)
- Heavy machinery (e.g., backhoes, cranes)
- Personal Protective Equipment (e.g., hard hats, harnesses, PPE)

DO NOT include personal life hazards. If a transcript flagged with [SAFETY_VIOLATION] contains mentions of "art", "paint", "canvas", "easel", "kids", "toddler", or "kitchen", it must be EXCLUDED entirely from the official report, as these are non-workplace items.
""")

    # 3. Generate Massive Waste-land of JSON Fragments
    start_date = datetime(2023, 9, 1)
    end_date = datetime(2023, 11, 30)
    
    # Hardcoded ground truth data for the target week (Oct 16 - Oct 22) for PROJ-77X-MUNI
    ground_truth = {
        "2023-10-16": "Monday. Scaffolding on the east wall is missing a guardrail, need to get that fixed ASAP. [SAFETY_VIOLATION] Also, mental note: I need to buy more cadmium red paint for the garage mural, almost ran out. The kids were surprisingly calm tonight. [HOURS=14]",
        "2023-10-17": "Tuesday. Kids were crying all morning, gave me a headache. Art hazard: The toddler tried to eat a blue crayon, crisis averted but it was close. [SAFETY_VIOLATION] Exposed wiring near the main water line in sector B. Very dangerous. [SAFETY_VIOLATION] [HOURS=20]",
        "2023-10-18": "Wednesday. Rained out early. No major site hazards today, thank God. Need to remember to pick up diapers on the way home. I left my wooden easel dangerously close to the driveway, almost backed over it with the truck. Gotta be more careful. [SAFETY_VIOLATION] [HOURS=8]",
        "2023-10-19": "Thursday. Good progress on the framing. Subcontractors were not wearing hard hats in the overhead drop zone. Yelled at them for that. [SAFETY_VIOLATION] The sunset was beautiful today, painted a quick watercolor sketch on my lunch break. [HOURS=22]",
        "2023-10-20": "Friday. End of the week, finally. Unsecured trench over 5 feet deep left overnight by the backhoe operator. [SAFETY_VIOLATION] Gotta write him up. The kids are finally asleep, going to work on my canvas now. [HOURS=16]"
    }

    # Decoy texts for noise generation
    decoy_texts = [
        "Just a routine check. Everything looks fine today.",
        "Need to order more cement for sector C tomorrow. [HOURS=10]",
        "Traffic was terrible this morning. Site looks okay. [HOURS=5]",
        "Forgot my lunch, had to buy a sandwich. Oh, the crane operator was late.",
        "The kitchen sink at home is leaking again, total disaster. [SAFETY_VIOLATION]",
        "Almost tripped over my kids' toys in the hallway. [SAFETY_VIOLATION]",
        "Finished the foundation pour. Looks solid. [HOURS=12]",
        "Just rambling here, trying to clear my head. The new canvas is looking good."
    ]
    
    current_date = start_date
    random.seed(42) # Ensuring reproducibility of the wasteland
    
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        year, month, day = current_date.strftime("%Y"), current_date.strftime("%m"), current_date.strftime("%d")
        
        # Create deeply nested directory
        daily_dir = os.path.join("voice_memos", year, month, day)
        os.makedirs(daily_dir, exist_ok=True)
        
        # Determine how many files to generate for this day (simulate fragmentation)
        num_files = random.randint(3, 8)
        
        for _ in range(num_files):
            file_id = str(uuid.uuid4())
            project_code = random.choice(["PROJ-101-RES", "PROJ-550-HWY", "PROJ-77X-MUNI", "PROJ-999-COM", "UNKNOWN"])
            
            # If this is a target day, inject the ground truth ONCE for the correct project
            if date_str in ground_truth and project_code == "PROJ-77X-MUNI":
                text = ground_truth.pop(date_str)
            else:
                text = random.choice(decoy_texts)
                # occasionally inject random hours and violations to decoys to confuse regex
                if random.random() > 0.7 and "[HOURS=" not in text:
                    text += f" [HOURS={random.randint(2, 12)}]"
                if random.random() > 0.8 and "[SAFETY_VIOLATION]" not in text:
                    text += " Just another issue to log. [SAFETY_VIOLATION]"
                    
            record = {
                "sync_id": file_id,
                "metadata": {
                    "device": "CloudDictate_Pro",
                    "timestamp": f"{date_str}T{random.randint(8,18):02d}:{random.randint(0,59):02d}:00Z",
                    "tagged_project": project_code
                },
                "transcription": text,
                "confidence_score": round(random.uniform(0.7, 0.99), 2)
            }
            
            # Scatter JSON structure randomly to prevent simple bash grep
            if random.random() > 0.5:
                # Shuffle the dictionary keys conceptually by dumping with different sorts or structures
                record = {"transcription": text, "metadata": record["metadata"], "sync_id": file_id}

            filepath = os.path.join(daily_dir, f"memo_{file_id[:8]}.json")
            with open(filepath, "w") as f:
                json.dump(record, f, indent=2)
                
        current_date += timedelta(days=1)

if __name__ == "__main__":
    build_env()
