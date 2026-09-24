import os
import argparse
import json
import csv

def build_turn_1():
    os.makedirs("market_reports", exist_ok=True)
    os.makedirs("compliance", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # Market Research Data
    demo_data = {
        "report_id": "Q3_DERMA",
        "primary_target": {
            "gender": "Female",
            "age_range": "30-45",
            "min_audience_income_usd": 100000
        },
        "kpi_requirements": {
            "min_engagement_rate_percent": 4.5
        }
    }
    with open("market_reports/demographics.json", "w") as f:
        json.dump(demo_data, f, indent=4)

    # Compliance Data
    with open("compliance/fda_guidelines.txt", "w") as f:
        f.write("DERMAGENESIS COMPLIANCE DIRECTIVE\n")
        f.write("Due to the scientific nature of our R&D, we are strictly monitoring claims.\n")
        f.write("BANNED KEYWORDS IN ANY PROMOTIONAL POST SNIPPETS:\n")
        f.write("- miracle\n- cures\n- 100% safe\n- medical grade\n- prescription strength\n")

    # NA Influencers DB (Contains traps: best engagement fails compliance or demo)
    na_influencers = [
        {"handle": "@GlowUpJane", "gender": "Female", "age_demo": "20-29", "audience_income": 50000, "eng_rate": 6.0, "cost": 10000, "snippet": "Great product for daily use!"}, # Fails demo
        {"handle": "@ScienceSkin", "gender": "Female", "age_demo": "30-45", "audience_income": 120000, "eng_rate": 5.8, "cost": 25000, "snippet": "This is a miracle for wrinkles!"}, # Fails compliance
        {"handle": "@DrBeauty", "gender": "Female", "age_demo": "30-45", "audience_income": 110000, "eng_rate": 5.2, "cost": 30000, "snippet": "Love the peptide complex."}, # Pass. (Highest valid)
        {"handle": "@MomChic", "gender": "Female", "age_demo": "30-45", "audience_income": 105000, "eng_rate": 4.8, "cost": 20000, "snippet": "Keeps my skin hydrated on busy days."}, # Pass. (2nd valid)
        {"handle": "@LuxeLife", "gender": "Female", "age_demo": "30-45", "audience_income": 150000, "eng_rate": 4.6, "cost": 40000, "snippet": "Worth every penny for my routine."}, # Pass. (3rd valid - very expensive)
        {"handle": "@DermaDaily", "gender": "Female", "age_demo": "30-45", "audience_income": 130000, "eng_rate": 4.7, "cost": 15000, "snippet": "Good texture and absorption."}, # Pass. (4th valid - cheap backup)
        {"handle": "@BioHackerMom", "gender": "Female", "age_demo": "30-45", "audience_income": 115000, "eng_rate": 5.1, "cost": 22000, "snippet": "Basically prescription strength without the visit!"} # Fails compliance
    ]

    with open("influencers_na.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["handle", "gender", "age_demo", "audience_income", "eng_rate", "cost", "snippet"])
        writer.writeheader()
        writer.writerows(na_influencers)

def build_turn_2():
    os.makedirs("eu_expansion", exist_ok=True)
    os.makedirs("inbox", exist_ok=True)

    # Inbox Update - Budget cut
    with open("inbox/finance_budget_update.eml", "w") as f:
        f.write("From: finance@rnd-corp.com\n")
        f.write("To: Marketing Manager\n")
        f.write("Subject: URGENT: Q3 Global Budget Reduction\n\n")
        f.write("Due to R&D overruns on the DermaGenesis formula, your global launch budget (covering NA influencers, EU influencers, AND podcasts combined) is strictly capped at $110,000 USD.\n")
        f.write("Do not exceed this amount under any circumstances.\n")

    # EU Influencers DB
    eu_influencers = [
        {"handle": "@EuroGlow", "gender": "Female", "age_demo": "30-45", "audience_income": 110000, "eng_rate": 5.8, "cost": 35000, "snippet": "Très bien pour la peau."}, # Pass, but expensive
        {"handle": "@LondonSkin", "gender": "Female", "age_demo": "30-45", "audience_income": 105000, "eng_rate": 4.9, "cost": 10000, "snippet": "Literally medical grade skincare!"}, # Fails compliance
        {"handle": "@BerlinBeauty", "gender": "Female", "age_demo": "30-45", "audience_income": 120000, "eng_rate": 4.6, "cost": 15000, "snippet": "Wunderbar hydration."}, # Pass
        {"handle": "@ParisChic", "gender": "Female", "age_demo": "30-45", "audience_income": 140000, "eng_rate": 5.0, "cost": 20000, "snippet": "J'adore les peptides."}, # Pass
        {"handle": "@MilanStyle", "gender": "Female", "age_demo": "18-24", "audience_income": 90000, "eng_rate": 6.5, "cost": 12000, "snippet": "Bella!"} # Fails demo
    ]

    with open("eu_expansion/euro_influencers.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["handle", "gender", "age_demo", "audience_income", "eng_rate", "cost", "snippet"])
        writer.writeheader()
        writer.writerows(eu_influencers)

    # Podcasts Options
    podcasts = [
        {"name": "The Skincare Science", "cost": 10000, "listeners": 50000},
        {"name": "Fashion & Tech Weekly", "cost": 5000, "listeners": 20000},
        {"name": "Mom's Daily Podcast", "cost": 15000, "listeners": 80000}
    ]
    with open("eu_expansion/podcasts.json", "w") as f:
        json.dump(podcasts, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
