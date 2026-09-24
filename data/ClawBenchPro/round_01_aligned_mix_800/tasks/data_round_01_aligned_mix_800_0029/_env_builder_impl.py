import os
import argparse
import csv
import json

def build_turn_1():
    os.makedirs("authors", exist_ok=True)
    os.makedirs("archives", exist_ok=True)
    os.makedirs("admin", exist_ok=True)

    # submissions.csv
    # Trap: A02 is very cheap but NOT on whitelist. A06 is cheap but NOT on whitelist.
    authors_data = [
        ["author_id", "name", "genre", "fee"],
        ["A01", "Eleanor Vance", "Poetry", "500"],
        ["A02", "Jack Torrance", "Horror", "100"],
        ["A03", "Wendy Torrance", "Children", "600"],
        ["A04", "Paul Sheldon", "Romance", "1200"],
        ["A05", "Annie Wilkes", "Biography", "800"],
        ["A06", "Ben Mears", "Thriller", "200"],
        ["A07", "Susan Norton", "History", "900"],
        ["A08", "Danny Glick", "Poetry", "400"],
        ["A09", "Matt Burke", "Mystery", "700"],
        ["A10", "Mark Petrie", "Sci-Fi", "1000"]
    ]
    with open("authors/submissions.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(authors_data)

    # historical_docs.json
    # Trap: D04 is very cheap base cost, but "Fragile" makes it 3.0x -> 1200.
    # Trap: D05 is "Poor", which is forbidden in policy.
    docs_data = [
        {"doc_id": "D01", "title": "Town Charter 1890", "year": 1890, "condition": "Mint", "base_cost": 800},
        {"doc_id": "D02", "title": "Mayor's Diary 1920", "year": 1920, "condition": "Good", "base_cost": 600},
        {"doc_id": "D03", "title": "Library Blueprint 1850", "year": 1850, "condition": "Good", "base_cost": 1000},
        {"doc_id": "D04", "title": "Civil War Letters", "year": 1863, "condition": "Fragile", "base_cost": 400},
        {"doc_id": "D05", "title": "Old Mill Ledger", "year": 1905, "condition": "Poor", "base_cost": 100},
        {"doc_id": "D06", "title": "School Records 1950", "year": 1950, "condition": "Mint", "base_cost": 500},
        {"doc_id": "D07", "title": "Railroad Map 1888", "year": 1888, "condition": "Good", "base_cost": 700},
        {"doc_id": "D08", "title": "First Newspaper", "year": 1910, "condition": "Fragile", "base_cost": 300}
    ]
    with open("archives/historical_docs.json", "w") as f:
        json.dump(docs_data, f, indent=4)

    # policies.txt
    policy_content = """COUNTY ARCHIVES & LIBRARY POLICY - CONFIDENTIAL

1. APPROVED AUTHOR WHITELIST:
Only the following Author IDs have passed the county background check and may be hired:
[A01, A03, A04, A05, A07, A08, A09, A10]

2. DOCUMENT PRESERVATION MULTIPLIERS:
Handling historical documents requires special preservation procedures. 
The true cost of exhibiting a document is calculated as: (base_cost * condition_multiplier).
- "Mint" condition: 1.0 multiplier
- "Good" condition: 1.5 multiplier
- "Fragile" condition: 3.0 multiplier
Note: Documents in "Poor" condition are strictly forbidden from exhibition.

3. BUDGET:
The absolute maximum combined budget for the Main Exhibition Hall (Author fees + True Document Costs) is $3500.
"""
    with open("admin/policies.txt", "w") as f:
        f.write(policy_content)

def build_turn_2():
    # Remove policies.txt as per narrative
    if os.path.exists("admin/policies.txt"):
        os.remove("admin/policies.txt")
        
    # memo_turn2.txt
    memo_content = """FROM: County Director
TO: Library Assistant
SUBJECT: Branch Allocations

Great work on the main hall. Now, assign 1 author and 1 historical document to each of our 3 branches.
The maximum combined cost per branch (1 author + 1 document true cost) cannot exceed $1800. 
Do not reuse main hall selections. Ensure all previous background check and condition rules apply.
"""
    with open("admin/memo_turn2.txt", "w") as f:
        f.write(memo_content)

    # branch_requests.json
    branch_reqs = {
        "North": {
            "author_genre_preference": "Mystery",
            "document_year_max": 1900
        },
        "South": {
            "author_genre_preference": "History",
            "document_year_max": 1960
        },
        "East": {
            "author_genre_preference": "Poetry",
            "document_year_max": 1920
        }
    }
    with open("branch_requests.json", "w") as f:
        json.dump(branch_reqs, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
