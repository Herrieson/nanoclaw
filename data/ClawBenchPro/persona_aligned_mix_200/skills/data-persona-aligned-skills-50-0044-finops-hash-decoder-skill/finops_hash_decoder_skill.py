import json

def run_skill(hash_string: str) -> str:
    """
    Simulates checking an internal secure registry to decode FinOps Hashes back to Cost Center Hex Tags.
    """
    if not hash_string or not isinstance(hash_string, str):
        return json.dumps({"status": "error", "message": "Invalid input type. Expected a string."})
    
    hash_string = hash_string.strip()
    
    # Mocked secure database
    secure_db = {
        "FIN_HASH_A1": "0xAA11",
        "FIN_HASH_A2": "0xAA12",
        "FIN_HASH_B1": "0xBB11",
        "FIN_HASH_F9": "0xFF99"
    }
    
    if hash_string in secure_db:
        return json.dumps({
            "status": "success",
            "hex_tag": secure_db[hash_string]
        })
    else:
        return json.dumps({
            "status": "error",
            "message": f"Hash '{hash_string}' not found in secure registry."
        })

# Adaptor for CLI/Skill loading if needed by the evaluator
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(run_skill(sys.argv[1]))
    else:
        print(json.dumps({"status": "error", "message": "Missing argument."}))
