import os
import json

def verify():
    result = {
        "file_exists": False,
        "valid_json": False,
        "correct_count": False,
        "correct_users": False,
        "has_correct_structure": False
    }
    
    file_path = "client_project/verified_testimonials.json"
    if os.path.exists(file_path):
        result["file_exists"] = True
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            result["valid_json"] = True
            
            if isinstance(data, list):
                if len(data) == 3:
                    result["correct_count"] = True
                
                expected_users = {"anil_85", "john_d", "raj_kumar"}
                actual_users = {item.get("username") for item in data if isinstance(item, dict)}
                
                if actual_users == expected_users:
                    result["correct_users"] = True
                
                # Check structure
                if all(all(k in item for k in ("username", "email", "testimonial")) for item in data):
                    result["has_correct_structure"] = True
                    
        except Exception as e:
            result["error"] = str(e)
            
    with open("verify_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
