import os
import sys

def check_status(business_name):
    """
    Mock internal database for donor statuses.
    """
    pending_list = ["MegaCorp Oil", "Global Retailers LLC"]
    paid_list = ["Local Greenery", "Austin Tech Hub", "Mom & Pop Diner"]
    
    name = business_name.strip()
    if any(p.lower() in name.lower() for p in pending_list):
        return "Status: PENDING - Payment not received. Requires follow-up."
    elif any(p.lower() in name.lower() for p in paid_list):
        return "Status: PAID - Funds cleared on Aug 15th."
    else:
        return "Status: UNKNOWN - Business not found in pledge database."

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(check_status(sys.argv[1]))
