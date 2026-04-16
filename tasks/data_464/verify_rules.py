import os
import json
import math

def verify():
    base_dir = "."
    report_path = os.path.join(base_dir, "top_authors_report.json")
    
    state = {
        "file_exists": False,
        "valid_json": False,
        "is_list": False,
        "correct_authors": False,
        "correct_revenues": False,
        "correct_hugo_flags": False,
        "correct_sort_order": False
    }

    if not os.path.exists(report_path):
        with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
            json.dump(state, f)
        return

    state["file_exists"] = True

    try:
        with open(report_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        state["valid_json"] = True
    except:
        with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
            json.dump(state, f)
        return

    if isinstance(data, list):
        state["is_list"] = True
    else:
        with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
            json.dump(state, f)
        return

    # Expected Data Calculations:
    # Frank Herbert: (15.99 * 2) + (15.99 * 1) = 47.97 (Hugo: True)
    # J.R.R. Tolkien: 10.00 * 3 = 30.00 (Hugo: False)
    # Isaac Asimov: (12.50 * 1) + (12.50 * 2) = 37.50 (Hugo: True)
    # William Gibson: 14.00 * 2 = 28.00 (Hugo: True)
    # Ursula K. Le Guin: 16.50 * 1 = 16.50 (Hugo: True)
    # Brandon Sanderson: (20.00 * 2) + (25.00 * 1) = 65.00 (Hugo: False)
    # Neil Gaiman: 18.00 * 1 = 18.00 (Hugo: True)
    # Ignore: Harper Lee (Fiction), George Orwell (Dystopian)

    expected = {
        "Brandon Sanderson": {"revenue": 65.00, "is_hugo_winner": False},
        "Frank Herbert": {"revenue": 47.97, "is_hugo_winner": True},
        "Isaac Asimov": {"revenue": 37.50, "is_hugo_winner": True},
        "J.R.R. Tolkien": {"revenue": 30.00, "is_hugo_winner": False},
        "William Gibson": {"revenue": 28.00, "is_hugo_winner": True},
        "Neil Gaiman": {"revenue": 18.00, "is_hugo_winner": True},
        "Ursula K. Le Guin": {"revenue": 16.50, "is_hugo_winner": True}
    }

    try:
        authors_in_data = [item["author"] for item in data]
        if set(authors_in_data) == set(expected.keys()):
            state["correct_authors"] = True
            
            # Check revenues and hugo flags
            rev_ok = True
            hugo_ok = True
            for item in data:
                author = item["author"]
                expected_rev = expected[author]["revenue"]
                expected_hugo = expected[author]["is_hugo_winner"]
                
                if not math.isclose(item["revenue"], expected_rev, rel_tol=1e-4):
                    rev_ok = False
                if item["is_hugo_winner"] is not expected_hugo:
                    hugo_ok = False
            
            state["correct_revenues"] = rev_ok
            state["correct_hugo_flags"] = hugo_ok
            
            # Check sort order
            revenues = [item["revenue"] for item in data]
            if revenues == sorted(revenues, reverse=True):
                state["correct_sort_order"] = True

    except Exception as e:
        pass # Keys missing or wrong types

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
