import os
import argparse
import csv
import json

def build_turn_1():
    os.makedirs("financials", exist_ok=True)
    os.makedirs("dd_reports", exist_ok=True)

    # Base data definitions: ID, 2021 Rev, 2022 Rev, 2023 Rev, 2023 Profit, Asset_Type, Region, Cultural_Theme, DD_Risk
    projects = [
        ("P01", 100, 120, 150, 27, "Light", "North America", "Italian", "Clean background check."), # Margin 18%, Growth Yes -> PASS
        ("P02", 200, 190, 250, 50, "Heavy", "Asia", "Japanese", "Minor local complaints."), # No continuous growth -> FAIL
        ("P03", 80, 100, 200, 32, "Heavy", "Europe", "French", "All clear on legal front."), # Margin 16%, Growth Yes -> PASS (Turn 1). Poison for Turn 2.
        ("P04", 50, 70, 100, 25, "Light", "South America", "Mexican", "Warning: pending tax lawsuit noted."), # High margin, but lawsuit -> FAIL
        ("P05", 300, 320, 350, 40, "Light", "North America", "American", "No issues."), # Margin < 15% -> FAIL
        ("P06", 150, 160, 180, 18, "Heavy", "Europe", "German", "Management is stable."), # Margin 10% -> FAIL
        ("P07", 90, 110, 105, 20, "Light", "Asia", "Chinese", "Clean."), # No growth -> FAIL
        ("P08", 120, 150, 200, 40, "Light", "Europe", "Spanish", "Perfect compliance."), # Margin 20% -> PASS
        ("P09", 60, 65, 70, 8, "Light", "Africa", "Moroccan", "Some minor management dispute over trivial matters."), # Has dispute -> FAIL
        ("P10", 210, 230, 280, 35, "Heavy", "Asia", "Korean", "No legal issues."), # Margin 12.5% -> FAIL
        ("P11", 50, 40, 60, 12, "Light", "North America", "Caribbean", "Clean."), # No growth -> FAIL
        ("P12", 180, 200, 250, 42.5, "Light", "Asia", "Indian", "No issues found."), # Margin 17% -> PASS
        ("P13", 100, 110, 130, 18, "Heavy", "North America", "Greek", "Pending tax lawsuit from 2020."), # Lawsuit -> FAIL
        ("P14", 80, 90, 120, 16, "Light", "Europe", "British", "Clean."), # Margin 13.3% -> FAIL
        ("P15", 30, 50, 80, 16, "Heavy", "South America", "Peruvian", "Serious management dispute at board level."), # Dispute -> FAIL
        ("P16", 110, 140, 170, 20, "Light", "Asia", "Vietnamese", "Clean."), # Margin 11.7% -> FAIL
        ("P17", 95, 95, 100, 16, "Light", "North America", "Canadian", "Clean."), # No strict growth (95 to 95) -> FAIL
        ("P18", 220, 240, 260, 30, "Heavy", "Europe", "Russian", "Clean."), # Margin 11.5% -> FAIL
        ("P19", 140, 150, 190, 25, "Light", "Africa", "Ethiopian", "Clean."), # Margin 13.1% -> FAIL
        ("P20", 75, 85, 100, 14, "Heavy", "Asia", "Thai", "Clean.") # Margin 14% -> FAIL
    ]

    for p in projects:
        pid, r21, r22, r23, p23, ast, reg, theme, risk = p
        
        # Write Financials
        with open(f"financials/{pid}_financials.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Year", "Revenue", "Profit", "Asset_Type", "Region", "Cultural_Theme"])
            writer.writerow(["2021", r21, p23*0.6, ast, reg, theme])
            writer.writerow(["2022", r22, p23*0.8, ast, reg, theme])
            writer.writerow(["2023", r23, p23, ast, reg, theme])
            
        # Write DD Report
        with open(f"dd_reports/{pid}_dd.txt", "w") as f:
            f.write(f"Due Diligence Report for {pid}\n")
            f.write(f"Theme: {theme} Cuisine\n")
            f.write("-" * 20 + "\n")
            f.write("Risk Assessment:\n")
            f.write(risk + "\n")

def build_turn_2():
    # Write Policy Update
    policy_text = """CONFIDENTIAL - 2024 REGULATORY & MACRO POLICY UPDATE
Due to recent shifts in global compliance and inflationary pressures, the following adjustments must be applied retroactively to the 2023 financials for evaluation purposes:

1. Heavy Asset Penalty: Any project with Asset_Type "Heavy" must deduct 20% of its 2023 Profit as a compliance provision. (e.g., if Profit is 10, new profit is 8).
2. European Inflation Hit: Any project operating in Region "Europe" faces increased material costs. You must further deduct 5% of its ORIGINAL 2023 Profit.

Note: These are cumulative. If a project is both Heavy and Europe, it suffers both deductions from its original profit. Recalculate margins using the adjusted profit against the original 2023 Revenue.
"""
    with open("policy_update_2024.txt", "w") as f:
        f.write(policy_text)

    # Write New Proposals
    os.makedirs("new_proposals/financials", exist_ok=True)
    os.makedirs("new_proposals/dd_reports", exist_ok=True)

    new_projects = [
        # N01: PASS. Thai. 20->25->40, Profit 8. Margin 20%. Light/Asia. 
        ("N01", 20, 25, 40, 8, "Light", "Asia", "Thai", "Flawless audit."),
        # N02: FAIL due to forgotten memory. Margin is huge, but has dispute.
        ("N02", 50, 60, 80, 24, "Light", "North America", "American", "High yield, but severe management dispute underway."),
        # N03: PASS. Italian. 80->90->120, Profit 30. Margin 25%. Light/North America. (Will conflict with P01 later)
        ("N03", 80, 90, 120, 30, "Light", "North America", "Italian", "Clean records."),
        # N04: FAIL. Heavy + Europe penalty drops it below 15%. Rev 100, Profit 18 (Margin 18%). Penalty: 18*0.2 = 3.6, 18*0.05 = 0.9. Adj Profit = 13.5. Margin = 13.5%.
        ("N04", 70, 85, 100, 18, "Heavy", "Europe", "Greek", "No legal risk."),
        # N05: FAIL. No growth.
        ("N05", 150, 140, 180, 45, "Light", "Asia", "Korean", "Clean.")
    ]

    for p in new_projects:
        pid, r21, r22, r23, p23, ast, reg, theme, risk = p
        
        with open(f"new_proposals/financials/{pid}_financials.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Year", "Revenue", "Profit", "Asset_Type", "Region", "Cultural_Theme"])
            writer.writerow(["2021", r21, p23*0.6, ast, reg, theme])
            writer.writerow(["2022", r22, p23*0.8, ast, reg, theme])
            writer.writerow(["2023", r23, p23, ast, reg, theme])
            
        with open(f"new_proposals/dd_reports/{pid}_dd.txt", "w") as f:
            f.write(f"Due Diligence Report for {pid}\n")
            f.write(f"Theme: {theme} Cuisine\n")
            f.write("-" * 20 + "\n")
            f.write("Risk Assessment:\n")
            f.write(risk + "\n")

def build_turn_3():
    # Budget and ticket sizes
    # Valid candidates surviving Turn 2:
    # P01 (Italian): Adj Profit 27.
    # P08 (Spanish): Adj Profit 38 (40 - 40*0.05).
    # P12 (Indian): Adj Profit 42.5.
    # N01 (Thai): Adj Profit 8.
    # N03 (Italian): Adj Profit 30.
    
    # We want max profit under budget 100, with UNIQUE themes.
    # Ticket sizes:
    # P01: 40
    # P08: 50
    # P12: 30
    # N01: 20
    # N03: 60
    
    # If we greedily take N03(30) + P12(42.5) = cost 90, total profit 72.5
    # If we take P08(38) + P12(42.5) + N01(8) = cost 100, total profit 88.5. (Best combo!)
    # Notice P01 and N03 are both Italian. Can only pick one.
    
    budget_data = {
        "Total_Budget_Millions": 100,
        "Project_Ticket_Sizes_Millions": {
            "P01": 40,
            "P02": 20,
            "P03": 35,
            "P04": 25,
            "P05": 10,
            "P06": 15,
            "P07": 30,
            "P08": 50,
            "P09": 10,
            "P10": 40,
            "P11": 15,
            "P12": 30,
            "P13": 20,
            "P14": 25,
            "P15": 30,
            "P16": 15,
            "P17": 20,
            "P18": 45,
            "P19": 20,
            "P20": 25,
            "N01": 20,
            "N02": 30,
            "N03": 60,
            "N04": 25,
            "N05": 40
        }
    }
    
    with open("budget_directive.json", "w") as f:
        json.dump(budget_data, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
    elif args.turn == 3:
        build_turn_3()
