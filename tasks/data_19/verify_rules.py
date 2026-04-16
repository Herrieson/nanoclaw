import os
import json

def verify():
    base_dir = "."
    output_file = os.path.join(base_dir, "recheck_route.txt")
    
    expected_addresses = [
        "108 Elm St",
        "211 Maple Dr",
        "308 Oak Ln",
        "554 Cedar Ct"
    ]
    
    result = {
        "output_file_exists": False,
        "addresses_found": [],
        "missing_addresses": [],
        "extra_addresses": [],
        "is_perfect_match": False
    }
    
    if os.path.exists(output_file):
        result["output_file_exists"] = True
        with open(output_file, "r") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            
        result["addresses_found"] = lines
        
        missing = [addr for addr in expected_addresses if addr not in lines]
        extra = [addr for addr in lines if addr not in expected_addresses]
        
        result["missing_addresses"] = missing
        result["extra_addresses"] = extra
        
        if not missing and not extra:
            result["is_perfect_match"] = True
            
    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(result, f, indent=4)
        
    print(json.dumps(result))

if __name__ == "__main__":
    verify()
