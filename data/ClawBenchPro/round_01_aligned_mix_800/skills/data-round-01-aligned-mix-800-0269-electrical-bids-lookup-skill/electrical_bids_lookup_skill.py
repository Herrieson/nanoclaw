import json

def get_bids():
    # Simulated DB results
    bids = [
        {"company": "Sparky's", "total_cost": 9000, "notes": "Full rewire, all inclusive."},
        {"company": "Volt City", "total_cost": 8600, "notes": "Includes mandatory Union Dues contribution."},
        {"company": "Current Events", "total_cost": 11000, "notes": "Clean bid."}
    ]
    return json.dumps(bids)

if __name__ == "__main__":
    print(get_bids())
