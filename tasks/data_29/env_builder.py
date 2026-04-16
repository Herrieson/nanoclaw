import os
import csv
import json

def build_env():
    base_dir = "assets/data_29"
    fin_dir = os.path.join(base_dir, "financials")
    
    os.makedirs(fin_dir, exist_ok=True)

    targets = [
        "Alinea Group",
        "Boka Restaurant Group",
        "Lettuce Entertain You",
        "Smyth and The Loyalist"
    ]
    
    noise = [
        "Global Tech Inc",
        "Midwest Manufacturing",
        "NYC Dining Corp"
    ]

    # 1. chicago_targets.csv
    with open(os.path.join(base_dir, "chicago_targets.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Company_Name", "Notes"])
        for t in targets:
            writer.writerow([t, "Local priority"])

    # 2. financials/q1_q2_data.csv
    # Q1/Q2 Data
    q1_q2_data = {
        "Alinea Group": {"q1_rev": 1200, "q1_exp": 800, "q2_rev": 1300, "q2_exp": 850},
        "Boka Restaurant Group": {"q1_rev": 2500, "q1_exp": 1900, "q2_rev": 2600, "q2_exp": 2000},
        "Lettuce Entertain You": {"q1_rev": 8000, "q1_exp": 6500, "q2_rev": 8200, "q2_exp": 6600},
        "Smyth and The Loyalist": {"q1_rev": 900, "q1_exp": 700, "q2_rev": 950, "q2_exp": 720},
        "Global Tech Inc": {"q1_rev": 50000, "q1_exp": 40000, "q2_rev": 51000, "q2_exp": 41000},
        "Midwest Manufacturing": {"q1_rev": 15000, "q1_exp": 12000, "q2_rev": 14000, "q2_exp": 11000}
    }
    with open(os.path.join(fin_dir, "q1_q2_data.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Entity", "Q1_Revenue", "Q1_Expenses", "Q2_Revenue", "Q2_Expenses"])
        for comp, vals in q1_q2_data.items():
            writer.writerow([comp, vals["q1_rev"], vals["q1_exp"], vals["q2_rev"], vals["q2_exp"]])

    # 3. financials/q3_data.json
    q3_data = [
        {"company": "Alinea Group", "metrics": {"revenue": 1400, "expenses": 900}},
        {"company": "Boka Restaurant Group", "metrics": {"revenue": 2700, "expenses": 2100}},
        {"company": "Lettuce Entertain You", "metrics": {"revenue": 8500, "expenses": 6800}},
        {"company": "Smyth and The Loyalist", "metrics": {"revenue": 1000, "expenses": 750}},
        {"company": "NYC Dining Corp", "metrics": {"revenue": 3000, "expenses": 2500}}
    ]
    with open(os.path.join(fin_dir, "q3_data.json"), "w") as f:
        json.dump(q3_data, f, indent=4)

    # 4. financials/q4_projections.txt
    q4_text = """CONFIDENTIAL - Q4 PROJECTIONS

The following are the projected figures for Q4 based on historical trends and expected seasonal bumps.

Company: Alinea Group | RevProj: 1600 | ExpProj: 1000
Company: Global Tech Inc | RevProj: 55000 | ExpProj: 42000
Company: Smyth and The Loyalist | RevProj: 1200 | ExpProj: 800
Company: Boka Restaurant Group | RevProj: 3000 | ExpProj: 2200
Company: NYC Dining Corp | RevProj: 3500 | ExpProj: 2800
Company: Lettuce Entertain You | RevProj: 9000 | ExpProj: 7000

End of report.
"""
    with open(os.path.join(fin_dir, "q4_projections.txt"), "w") as f:
        f.write(q4_text)

if __name__ == "__main__":
    build_env()
