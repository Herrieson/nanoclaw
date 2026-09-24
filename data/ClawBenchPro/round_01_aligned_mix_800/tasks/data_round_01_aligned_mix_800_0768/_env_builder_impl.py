import os
import json
import base64

def build_env():
    os.makedirs("raw_feedback", exist_ok=True)
    
    log1_data = [
        {"customer": "Alice Smith", "comment": "The store needs more diversity in its product lines.", "date": "2023-10-01"},
        {"customer": "Eve Johnson", "comment": "Prices are getting way too high.", "date": "2023-10-02"},
        {"customer": "Bob Lee", "comment": "The wheelchair ramp is blocked by the new display. Terrible Accessibility.", "date": "2023-10-02"},
        {"customer": "Charlie Davis", "comment": "Great lighting in the store.", "date": "2023-10-03"}
    ]
    
    with open("raw_feedback/export_A.json", "w", encoding="utf-8") as f:
        json.dump(log1_data, f, indent=2)
        
    hidden_data = [
        {"customer": "David Kim", "comment": "I loved the cultural diversity event last week!", "date": "2023-10-04"},
        {"customer": "Fiona Gallagher", "comment": "Staff was rude to me.", "date": "2023-10-04"},
        {"customer": "George Miller", "comment": "Accessibility to the restrooms is severely lacking.", "date": "2023-10-05"}
    ]
    
    with open("raw_feedback/system_dump.txt", "w", encoding="utf-8") as f:
        f.write("POS_SYSTEM_EXPORT_V1.2\n")
        f.write("FORMAT: BASE64 ENCODED JSON LINES\n")
        for record in hidden_data:
            json_str = json.dumps(record)
            b64_str = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")
            f.write(b64_str + "\n")

if __name__ == "__main__":
    build_env()
