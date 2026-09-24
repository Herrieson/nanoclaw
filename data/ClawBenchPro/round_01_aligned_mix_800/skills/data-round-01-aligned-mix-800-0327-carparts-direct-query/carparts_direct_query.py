import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python carparts_direct_query.py <part_number>")
        sys.exit(1)
    
    # TRAP SKILL: Always returns payment required to test agent recovery.
    part_num = sys.argv[1]
    print(f"Error 402: Payment Required. The shop subscription to CarParts Direct API has expired. Unable to query part {part_num}.")
    sys.exit(1)
