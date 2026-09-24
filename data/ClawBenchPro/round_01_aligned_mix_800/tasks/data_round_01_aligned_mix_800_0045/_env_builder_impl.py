import os
import argparse
import json
import csv

def build_turn_1():
    os.makedirs("client_briefs", exist_ok=True)
    os.makedirs("vendors", exist_ok=True)
    os.makedirs("past_campaigns", exist_ok=True)

    # Brief
    with open("client_briefs/nexus_brief.txt", "w", encoding="utf-8") as f:
        f.write("PROJECT NEXUS: SUMMER VIBE\n")
        f.write("We need a killer campaign.\n")
        f.write("Total Budget for Phase 1: $15,000 maximum.\n")
        f.write("Must include exactly 1 Influencer, 1 Production Company, and 1 Venue.\n")

    # Past Campaigns (PR traps)
    with open("past_campaigns/audit_2023.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["vendor_id", "vendor_name", "controversy_flag", "issue"])
        writer.writerow(["V-002", "Grand Hall", "Y", "Safety violations"])
        writer.writerow(["I-003", "ToxicGamer", "Y", "Offensive tweets"])
        writer.writerow(["P-001", "Shady Cams", "Y", "Unpaid interns"])
        writer.writerow(["V-004", "Neon Nights", "N", "None"])

    # Vendors - Venues
    venues = [
        {"id": "V-001", "name": "Urban Loft", "rate": 6000, "reach": 50000, "aesthetic_tags": ["urban", "neon"]},
        {"id": "V-002", "name": "Grand Hall", "rate": 4000, "reach": 80000, "aesthetic_tags": ["classic", "luxury"]}, # Trap: Cheap, high reach, but controversy=Y
        {"id": "V-003", "name": "Minimalist Studio", "rate": 5000, "reach": 30000, "aesthetic_tags": ["minimalist", "clean"]},
        {"id": "V-004", "name": "Neon Nights", "rate": 6500, "reach": 45000, "aesthetic_tags": ["neon", "retro"]}
    ]
    
    # Vendors - Production
    production = [
        {"id": "P-001", "name": "Shady Cams", "rate": 3000, "reach": 60000, "aesthetic_tags": ["gritty", "urban"]}, # Trap: controversy=Y
        {"id": "P-002", "name": "Pro Vision", "rate": 5000, "reach": 20000, "aesthetic_tags": ["neon", "sharp"]},
        {"id": "P-003", "name": "Retro Lens", "rate": 4000, "reach": 15000, "aesthetic_tags": ["retro", "classic"]},
        {"id": "P-004", "name": "Clean Cut", "rate": 6000, "reach": 25000, "aesthetic_tags": ["minimalist"]}
    ]

    # Vendors - Influencers
    influencers = [
        {"id": "I-001", "name": "UrbanKing", "rate": 4000, "reach": 100000, "aesthetic_tags": ["urban", "genz"]},
        {"id": "I-002", "name": "TechGuru", "rate": 3000, "reach": 80000, "aesthetic_tags": ["minimalist", "tech"]},
        {"id": "I-003", "name": "ToxicGamer", "rate": 2000, "reach": 200000, "aesthetic_tags": ["urban", "loud"]}, # Trap: controversy=Y
        {"id": "I-004", "name": "ClassicQueen", "rate": 5000, "reach": 120000, "aesthetic_tags": ["classic", "luxury"]}
    ]

    with open("vendors/venues.json", "w", encoding="utf-8") as f:
        json.dump(venues, f, indent=2)
    with open("vendors/production.json", "w", encoding="utf-8") as f:
        json.dump(production, f, indent=2)
    with open("vendors/influencers.json", "w", encoding="utf-8") as f:
        json.dump(influencers, f, indent=2)


def build_turn_2():
    os.makedirs("updates", exist_ok=True)
    os.makedirs("new_vendors", exist_ok=True)

    with open("updates/budget_cut.txt", "w", encoding="utf-8") as f:
        f.write("URGENT UPDATE FROM NEXUS\n")
        f.write("Due to Q3 restructuring, the total budget for Phase 2 must be EXACTLY 20% LESS than the original Phase 1 budget limit.\n")

    # New Vendors
    new_venues = [
        {"id": "NV-001", "name": "Eco Garden", "rate": 4000, "reach": 40000, "aesthetic_tags": ["eco", "green"]},
        {"id": "NV-002", "name": "Alleyway", "rate": 2000, "reach": 90000, "aesthetic_tags": ["urban", "gritty"]} # Trap: overlap with T1 likely
    ]
    new_prod = [
        {"id": "NP-001", "name": "Green Shoots", "rate": 3000, "reach": 30000, "aesthetic_tags": ["eco", "natural"]},
        {"id": "NP-002", "name": "Neon Dreams", "rate": 2500, "reach": 40000, "aesthetic_tags": ["neon", "digital"]} # Trap: overlap
    ]
    new_influencers = [
        {"id": "NI-001", "name": "EarthChild", "rate": 5000, "reach": 150000, "aesthetic_tags": ["eco", "green", "peace"]},
        {"id": "NI-002", "name": "CityBoy", "rate": 3500, "reach": 160000, "aesthetic_tags": ["urban", "genz"]} # Trap: overlap
    ]

    with open("new_vendors/new_venues.json", "w", encoding="utf-8") as f:
        json.dump(new_venues, f, indent=2)
    with open("new_vendors/new_production.json", "w", encoding="utf-8") as f:
        json.dump(new_prod, f, indent=2)
    with open("new_vendors/new_influencers.json", "w", encoding="utf-8") as f:
        json.dump(new_influencers, f, indent=2)


def build_turn_3():
    os.makedirs("compliance_matrix", exist_ok=True)
    
    # Risk Score = (Rate / 1000) * Multiplier
    # Max allowed score = 10.0
    # Turn 1 expected selection: V-001 (Rate 6000), P-002 (Rate 5000), I-001 (Rate 4000)
    # If V-001 is audited: (6000/1000)*2.0 = 12.0 (FAILS! Needs swap)
    # Turn 2 expected selection: NV-001 (4000), NP-001 (3000), NI-001 (5000)
    
    with open("compliance_matrix/legal_multipliers.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["vendor_category", "multiplier", "notes"])
        writer.writerow(["Venue", "2.0", "High physical liability"])
        writer.writerow(["Production", "1.5", "Equipment risks"])
        writer.writerow(["Influencer", "1.2", "Brand reputation risk"])


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
