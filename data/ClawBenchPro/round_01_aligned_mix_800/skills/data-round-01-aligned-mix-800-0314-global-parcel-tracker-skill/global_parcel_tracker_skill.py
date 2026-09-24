import sys
import argparse
import json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--order_id", required=True)
    args = parser.parse_args()

    # Mock tracking data
    tracking_data = {
        "ORD-110": {"delay_days": 5, "status": "In Transit"},
        "ORD-111": {"delay_days": 4, "status": "Delayed"},
        "ORD-112": {"delay_days": 2, "status": "Pending Customs"},
        "ORD-113": {"delay_days": 6, "status": "Delayed"},
        "ORD-114": {"delay_days": 0, "status": "Delivered"}
    }

    result = tracking_data.get(args.order_id)
    if result:
        print(json.dumps(result))
    else:
        print(json.dumps({"error": "Order ID not found in global database."}))

if __name__ == "__main__":
    main()
