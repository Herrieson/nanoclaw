import os
import argparse
import json
import csv

def build_turn_1():
    os.makedirs("clients", exist_ok=True)
    os.makedirs("materials", exist_ok=True)
    os.makedirs("subcontractors", exist_ok=True)

    # Client specs
    with open("clients/bungee_tower.json", "w") as f:
        json.dump({
            "project_name": "Skyline Bungee Jump Tower",
            "required_phases": ["Foundation", "Framework", "Rigging"],
            "client_contact": "ThrillSeekers Inc."
        }, f, indent=4)

    # Material Catalog
    # M01: Grade A, $300 (High quality, expensive)
    # M02: Grade B, $100 (Medium quality, cheap)
    # M03: Grade C, $50  (Low quality, illegal in Turn 1)
    # M04: Grade A, $200 (High quality, medium cost)
    with open("materials/catalog.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["MaterialID", "Grade", "UnitCost"])
        writer.writerow(["M01", "A", 300])
        writer.writerow(["M02", "B", 100])
        writer.writerow(["M03", "C", 50])
        writer.writerow(["M04", "A", 200])

    # Subcontractors Turn 1
    # TRAP: Epsilon uses Grade C (Banned T1)
    # TRAP: Delta is valid Grade A for Rigging, but costs 45k, busting the 85k total budget if used in T1 or T2.
    # WINNER T1: Alpha (35k) + Beta (20k) + Gamma (15k) = 70k. (Gamma uses Grade B for Rigging, which becomes illegal in T2)
    subs = {
        "sub_alpha.yaml": "name: Alpha Constructors\nphase: Foundation\nhourly_rate: 200\nmaterial_id: M01\n",
        "sub_beta.yaml": "name: Beta Beams\nphase: Framework\nhourly_rate: 150\nmaterial_id: M02\n",
        "sub_gamma.yaml": "name: Gamma Ropes\nphase: Rigging\nhourly_rate: 100\nmaterial_id: M02\n",
        "sub_delta.yaml": "name: Delta Drop\nphase: Rigging\nhourly_rate: 250\nmaterial_id: M04\n",
        "sub_epsilon.yaml": "name: Epsilon Excavations\nphase: Foundation\nhourly_rate: 50\nmaterial_id: M03\n"
    }

    for filename, content in subs.items():
        with open(os.path.join("subcontractors", filename), "w") as f:
            f.write(content)

def build_turn_2():
    # Assume workspace carries over Turn 1 state
    os.makedirs("subcontractors/late_bids", exist_ok=True)

    # New Regulations
    with open("clients/new_regs.txt", "w") as f:
        f.write("ZONING BOARD EMERGENCY DECREE:\n")
        f.write("Due to recent safety concerns at extreme sports facilities, the use of Structural Grade 'B' materials is now STRICTLY PROHIBITED for any 'Rigging' phase of construction. Grade 'A' materials must be used for Rigging. Other phases are unaffected by this specific decree.\n")

    # Late Bids
    # Zeta: Rigging, $150/hr, M04. Cost: 15k + 10k = 25k. 
    # New Total with Alpha(35k) + Beta(20k) + Zeta(25k) = 80k. Fits the 85k budget!
    # Omega: Framework, $300/hr, M04. Cost: 30k + 10k = 40k. (Distraction)
    late_subs = {
        "sub_zeta.yaml": "name: Zeta Zenith\nphase: Rigging\nhourly_rate: 150\nmaterial_id: M04\n",
        "sub_omega.yaml": "name: Omega Outfitting\nphase: Framework\nhourly_rate: 300\nmaterial_id: M04\n"
    }

    for filename, content in late_subs.items():
        with open(os.path.join("subcontractors/late_bids", filename), "w") as f:
            f.write(content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
