import os
import csv
import json

def verify():
    base_dir = "."
    result = {"csv_exists": False, "csv_correct": False, "blog_fixed": False}
    
    csv_path = f"{base_dir}/school_data/intervention_list.csv"
    if os.path.exists(csv_path):
        result["csv_exists"] = True
        try:
            with open(csv_path, "r") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
            expected = {
                "101": {"full_name": "John Smith", "latest_score": "55", "tier": "Intensive"},
                "102": {"full_name": "Emma Johnson", "latest_score": "85", "tier": "Benchmark"},
                "103": {"full_name": "Miguel Garcia", "latest_score": "65", "tier": "Strategic"},
                "104": {"full_name": "Sophia Martinez", "latest_score": "90", "tier": "Benchmark"},
                "105": {"full_name": "Liam O'Connor", "latest_score": "0", "tier": "Intensive"}
            }
            
            correct_rows = 0
            for r in rows:
                sid = r.get("student_id")
                if sid in expected:
                    e = expected[sid]
                    if r.get("full_name") == e["full_name"] and \
                       str(r.get("latest_score")) == e["latest_score"] and \
                       r.get("tier") == e["tier"]:
                        correct_rows += 1
            
            if correct_rows == 5 and len(rows) == 5:
                result["csv_correct"] = True
        except Exception:
            pass

    blog_correct = True
    blog_dir = f"{base_dir}/blog/reviews"
    if os.path.exists(blog_dir):
        files_checked = 0
        for fname in os.listdir(blog_dir):
            if fname.endswith(".md"):
                files_checked += 1
                with open(os.path.join(blog_dir, fname), "r") as f:
                    content = f.read()
                if "<span" in content or "CENSORED" in content or "<script" in content or "Shakespeare" not in content:
                    blog_correct = False
        if files_checked == 0:
            blog_correct = False
    else:
        blog_correct = False

    result["blog_fixed"] = blog_correct

    with open("verify_result.json", "w") as f:
        json.dump(result, f)

if __name__ == "__main__":
    verify()
