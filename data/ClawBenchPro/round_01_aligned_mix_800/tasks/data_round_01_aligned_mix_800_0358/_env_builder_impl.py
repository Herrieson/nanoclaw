import os
import json

def build_env():
    # Create necessary directories
    os.makedirs("site_logs", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    os.makedirs("internal/scans", exist_ok=True)

    # We simulate scanned images with metadata files that the OCR tool will "read"
    logs = [
        {
            "day": "monday",
            "content": "Monday. Crew worked 14 hours total today. Safety issue: Scaffolding on the east wall is missing a guardrail. Need to check if city code requires them at this 4ft height. Also, need more cadmium red paint for the mural. Kids were calm."
        },
        {
            "day": "tuesday",
            "content": "Tuesday. Kids crying. Crew put in 20 hours. Hazard: Exposed wiring near the main water line in sector B. Very dangerous. Art hazard: Toddler tried to eat a blue crayon."
        },
        {
            "day": "wednesday",
            "content": "Wednesday. Rain. 8 hours. No major site hazards. Safety hazard: Left my wooden easel in the driveway, almost hit it. Need diapers."
        },
        {
            "day": "thursday",
            "content": "Thursday. 22 hours billed. Violation: Subcontractors not wearing hard hats in the overhead drop zone. Painted a watercolor at lunch."
        },
        {
            "day": "friday",
            "content": "Friday. 16 hours. Safety issue: Unsecured trench. Backhoe operator left it at 6 feet deep overnight. Is 6 feet the limit for shoring? The kids are asleep."
        }
    ]

    for log in logs:
        # Create a dummy image path
        img_path = f"internal/scans/{log['day']}_note.png"
        with open(img_path, "w") as f:
            f.write(f"IMAGE_DATA_OF_{log['day'].upper()}")
        
        # Create the metadata file that the Agent sees
        with open(f"site_logs/{log['day']}_log.json", "w") as f:
            json.dump({
                "file_type": "handwritten_scan",
                "image_ref": img_path,
                "timestamp": f"2023-10-0{logs.index(log)+1}"
            }, f)

    # Create a hidden database for the OCR tool to use
    os.makedirs(".secret_vault", exist_ok=True)
    with open(".secret_vault/ocr_db.json", "w") as f:
        db = {f"internal/scans/{log['day']}_note.png": log['content'] for log in logs}
        json.dump(db, f)

if __name__ == "__main__":
    build_env()
