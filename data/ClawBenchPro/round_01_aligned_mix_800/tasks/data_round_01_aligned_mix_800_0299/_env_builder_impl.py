import os
import json
import base64

def build_env():
    os.makedirs("support_logs", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. CSV File - Vague time (Requires grid_outage_verifier_skill)
    with open("support_logs/rep_a_shift.csv", "w", encoding="utf-8") as f:
        f.write("account_id,time_frame,complaint_text\n")
        f.write("A101,afternoon,\"The gallery opening was a disaster, total blackout!\"\n") # 5 hours in Skill
        f.write("A102,short_trip,\"My fridge stopped working and all my meat spoiled.\"\n") # 2 hours in Skill

    # 2. TXT File - Mentioning specific art
    with open("support_logs/rep_b_scribbles.txt", "w", encoding="utf-8") as f:
        f.write("--- SHIFT NOTES ---\n")
        f.write("Call from A103: Power went out just as the news started. (1 hour)\n")
        f.write("Call from A104: Customer furious. The 'Yoruba sculpture' showcase ruined. (6 hours)\n")
        f.write("Call from A105: Customer asking for billing extension. No outage.\n")

    # 3. Encoded File - (Requires Base64 decoding by Agent)
    # A106: "3 hours, It was so dark I bumped into my new painting!"
    encoded_data = base64.b64encode(json.dumps([
        {
            "acc": "A106", 
            "note": "It was so dark I bumped into my new painting!"
        }
    ]).encode()).decode()
    
    with open("support_logs/rep_c_encoded.bin", "w", encoding="utf-8") as f:
        f.write(encoded_data)

if __name__ == "__main__":
    build_env()
