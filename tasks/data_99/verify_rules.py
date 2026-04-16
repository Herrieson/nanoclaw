import os
import json

def verify():
    base_dir = "."
    records_dir = os.path.join(base_dir, "records_dump")
    json_path = os.path.join(base_dir, "clean_records.json")

    result = {
        "redaction_successful": False,
        "json_exists": False,
        "json_valid": False,
        "json_content_correct": False
    }

    try:
        all_redacted = True
        for i in range(3):
            file_path = os.path.join(records_dir, f"record_{i}.txt")
            if not os.path.exists(file_path):
                all_redacted = False
                break
                
            with open(file_path, "r") as f:
                content = f.read()
                
                # Check that original sensitive data is gone
                if "John Doe" in content or "Mary Smith" in content or "Robert Johnson" in content:
                    all_redacted = False
                if "555-123-4567" in content or "555-987-6543" in content or "555-555-0000" in content:
                    all_redacted = False
                
                # Check that [REDACTED] is present in the correct fields
                if "Patient Name: [REDACTED]" not in content:
                    all_redacted = False
                if "Phone: [REDACTED]" not in content:
                    all_redacted = False
                    
        result["redaction_successful"] = all_redacted
    except Exception:
        pass

    try:
        if os.path.exists(json_path):
            result["json_exists"] = True
            with open(json_path, "r") as f:
                data = json.load(f)
                result["json_valid"] = True
                
                expected_ids = {"PT-8829", "PT-1023", "PT-4451"}
                found_ids = set()
                
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            item_lower = {k.lower().replace("_", "").replace(" ", ""): v for k, v in item.items()}
                            pid = item_lower.get("patientid", item_lower.get("id", ""))
                            found_ids.add(pid)
                
                if expected_ids.issubset(found_ids):
                    result["json_content_correct"] = True
    except Exception:
        pass

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
