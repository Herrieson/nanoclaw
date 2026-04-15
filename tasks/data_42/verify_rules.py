import os
import json
import re

def verify():
    result = {
        "is_success": False,
        "score": 0,
        "physical_state_passed": False,
        "discrepancies_found": [],
        "details": ""
    }
    
    target_file = "bank_inquiry.txt" # Expecting it in the agent's root working directory
    
    if not os.path.exists(target_file):
        result["details"] = "Failed: target file 'bank_inquiry.txt' not found."
        write_result(result)
        return
        
    result["physical_state_passed"] = True
    
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Check if the missing/mismatched transaction IDs are mentioned
    has_tx_9002 = "TX-9002" in content
    has_tx_9004 = "TX-9004" in content
    
    if has_tx_9002: result["discrepancies_found"].append("TX-9002")
    if has_tx_9004: result["discrepancies_found"].append("TX-9004")
    
    # Simple heuristic scoring for the rule-based part
    if has_tx_9002 and has_tx_9004:
        result["score"] = 50 # 50 points from rules, 50 points from LLM judge
        result["is_success"] = True
        result["details"] = "All discrepancies successfully identified in the drafted document."
    else:
        result["score"] = len(result["discrepancies_found"]) * 25
        result["details"] = f"Partial success. Found: {result['discrepancies_found']}."

    write_result(result)

def write_result(data):
    with open('verify_result.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    verify()
