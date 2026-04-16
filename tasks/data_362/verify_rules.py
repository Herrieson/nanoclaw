import os
import json

def verify():
    bid_file = "bids/bid.txt"
    state = {
        "bid_file_exists": False,
        "contains_name": False,
        "contains_target_id": False,
        "contains_wrong_id": False,
        "contains_price": False
    }
    
    if os.path.exists(bid_file):
        state["bid_file_exists"] = True
        with open(bid_file, "r") as f:
            content = f.read().lower()
            if "carlos" in content:
                state["contains_name"] = True
            
            # The correct target ID is ART-992
            if "art-992" in content:
                state["contains_target_id"] = True
                
            # Check for trap IDs
            if "art-445" in content or "art-123" in content:
                state["contains_wrong_id"] = True
                
            # Check for the specified bid amount
            if "15000" in content or "15,000" in content:
                state["contains_price"] = True
                
    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
