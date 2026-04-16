import os
import json

def verify():
    base_dir = "."
    target_file = os.path.join(base_dir, "final_order.json")
    
    result = {
        "file_exists": False,
        "valid_json": False,
        "approved_orders_correct": False,
        "rejected_grades_correct": False,
        "actual_approved": None,
        "actual_rejected": None,
        "expected_approved": {
            "Charlotte's Web": 6,
            "The Hobbit": 2,
            "1984": 4,
            "Fahrenheit 451": 3,
            "To Kill a Mockingbird": 10
        },
        "expected_rejected": ["Grade 9"]
    }

    if os.path.exists(target_file):
        result["file_exists"] = True
        try:
            with open(target_file, "r") as f:
                data = json.load(f)
            result["valid_json"] = True
            
            actual_approved = data.get("approved_orders", {})
            actual_rejected = data.get("rejected_grades", [])
            
            result["actual_approved"] = actual_approved
            result["actual_rejected"] = actual_rejected
            
            # Check approved
            if actual_approved == result["expected_approved"]:
                result["approved_orders_correct"] = True
                
            # Check rejected
            if isinstance(actual_rejected, list) and sorted(actual_rejected) == sorted(result["expected_rejected"]):
                result["rejected_grades_correct"] = True
                
        except Exception as e:
            result["error"] = str(e)

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
