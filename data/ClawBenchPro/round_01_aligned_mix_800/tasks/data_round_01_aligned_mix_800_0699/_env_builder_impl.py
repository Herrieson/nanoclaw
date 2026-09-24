import os
import json

def build_env():
    os.makedirs("support_logs", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. CSV File - Easy parsing
    with open("support_logs/rep_a_shift.csv", "w", encoding="utf-8") as f:
        f.write("account_id,hours_out,complaint_text\n")
        f.write("A101,5,\"The gallery opening was a disaster, total blackout for hours!\"\n")
        f.write("A102,2,\"My fridge stopped working and all my meat spoiled.\"\n")

    # 2. TXT File - Unstructured notes
    with open("support_logs/rep_b_scribbles.txt", "w", encoding="utf-8") as f:
        f.write("--- SHIFT NOTES ---\n")
        f.write("Call from A103: Power outage lasted exactly 1 hour. Customer wants compensation.\n")
        f.write("Call from A104: Customer was furious! Outage was 6 hours long. The Yoruba sculpture showcase was completely ruined due to lack of lighting.\n")
        f.write("Call from A105: Customer just asking for a billing extension due to job loss. No outage reported.\n")

    # 3. JSON File - Different structure
    with open("support_logs/system_dump.json", "w", encoding="utf-8") as f:
        json.dump([
            {
                "acc": "A106", 
                "outage_duration_hrs": 3, 
                "customer_notes": "It was so dark I bumped into my new painting and tore the canvas!"
            }
        ], f, indent=2)

if __name__ == "__main__":
    build_env()
