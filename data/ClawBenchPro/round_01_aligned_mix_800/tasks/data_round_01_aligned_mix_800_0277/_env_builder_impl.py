import os
import json
import base64

def build_env():
    # Ensure dependencies for LLM Mock are available (failsafe)
    os.system("pip install openai httpx")
    
    # Create directories
    os.makedirs("records", exist_ok=True)
    
    # 1. Overtime Claims (JSON) - Contains a "Ghost" (Marcus Vane)
    overtime_claims = [
        {"name": "Bernice Thompson", "hours": 15.5}, # High Fatigue
        {"name": "Althea Richards", "hours": 8.0},
        {"name": "Marcus Vane", "hours": 10.0},      # GHOST
        {"name": "Cedric Miller", "hours": 5.25}
    ]
    with open("records/overtime_claims.json", "w") as f:
        json.dump(overtime_claims, f)

    # 2. Medication Logs (Proprietary .mcl format) - Contains another "Ghost" (Sheila Reed)
    med_logs_text = (
        "2023-10-01 08:00 - Bernice Thompson - Administered Insulin\n"
        "2023-10-01 09:30 - Sheila Reed - Administered Morphine\n" # GHOST
        "2023-10-01 10:15 - Darnell Williams - Administered Ibuprofen\n"
        "2023-10-01 11:00 - Althea Richards - Administered Saline"
    )
    # Encode into fake proprietary format
    encoded_bytes = base64.b64encode(med_logs_text.encode('utf-8')).decode('utf-8')
    mcl_content = f"MCL_SECURE_FORMAT_{encoded_bytes}"
    
    with open("records/medication_logs.mcl", "w") as f:
        f.write(mcl_content)

    # Add a distractor file
    with open("records/notes.txt", "w") as f:
        f.write("Need to order more bandages and hibiscus fertilizer. Also, remind IT to fix the HR portal!")

if __name__ == "__main__":
    build_env()
