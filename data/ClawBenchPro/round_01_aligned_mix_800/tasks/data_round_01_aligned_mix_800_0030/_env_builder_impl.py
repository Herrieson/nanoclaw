import os
import argparse
import json

def build_turn_1():
    os.makedirs("proposals", exist_ok=True)
    os.makedirs("curriculum_status", exist_ok=True)
    
    proposals = [
        {
            "id": "P001",
            "title": "Adriatic Ecology Workshop",
            "provider": "EcoDalmatia",
            "cost": 8500,
            "tags": ["nature", "ecology", "community service"],
            "description": "A deep dive into the Adriatic coast's biodiversity. Includes interdisciplinary links to biology and history.",
            "background": "An independent NGO focused on Mediterranean flora."
        },
        {
            "id": "P002",
            "title": "Zagreb Business Challenge",
            "provider": "ProfitMax Ed",
            "cost": 5000,
            "tags": ["business", "competition"],
            "description": "A high-stakes commercial competition for students to simulate startup funding.",
            "background": "Subsidiary of Global Corp."
        },
        {
            "id": "P003",
            "title": "History of Croatian Puppetry",
            "provider": "CultureArt",
            "cost": 7200,
            "tags": ["art", "history"],
            "description": "Learning traditional puppet making. Highly focused on artistic skills only.",
            "background": "Local artisan collective."
        },
        {
            "id": "P004",
            "title": "Balkan Heritage Gardening",
            "provider": "GreenRoots",
            "cost": 9000,
            "tags": ["nature", "community service", "interdisciplinary"],
            "description": "Integrating botany with Slavic folklore. Students build a community garden.",
            "background": "Affiliated with Balkan Botanical Society."
        },
        {
            "id": "P005",
            "title": "Modern Adriatic Science",
            "provider": "EcoDalmatia",
            "cost": 8200,
            "tags": ["nature", "ecology"],
            "description": "A scientific study of Adriatic marine life. 80% similarity to P001 in curriculum content.",
            "background": "An independent NGO."
        }
    ]
    
    for p in proposals:
        with open(f"proposals/{p['id']}.json", "w") as f:
            json.dump(p, f, indent=4)

def build_turn_2():
    os.makedirs("new_updates", exist_ok=True)
    # New proposals that might be better but have hidden issues
    updates = [
        {
            "id": "P006",
            "title": "Coastal Architecture & Math",
            "provider": "BuildFuture",
            "cost": 6000,
            "tags": ["interdisciplinary", "math", "history"],
            "description": "Calculating the structural integrity of ancient stone walls. Truly cross-subject.",
            "background": "Owned by StoneHoldings Inc."
        },
        {
            "id": "P007",
            "title": "The Empathy Project",
            "provider": "KindnessFound",
            "cost": 12000,
            "tags": ["community service", "interdisciplinary"],
            "description": "A complex social study program focusing on refugee stories in the Balkans.",
            "background": "Charity branch of MegaLogistics."
        }
    ]
    for p in updates:
        with open(f"new_updates/{p['id']}.json", "w") as f:
            json.dump(p, f, indent=4)

def build_turn_3():
    # Adding the final constraint: the blacklist
    with open("vendor_blacklist.txt", "w") as f:
        f.write("StoneHoldings Inc.\nMegaLogistics\nGlobal Corp.")
    
    # Adding a hidden 'backup' file that was 'previously rejected' due to budget in Turn 1
    # This represents the "edge case" where budget can be stretched.
    backup = {
        "id": "P008",
        "title": "The Peace Garden Initiative",
        "provider": "PureHeart Foundation",
        "cost": 9800, # This might cause a slight over-budget if added late
        "tags": ["nature", "community service", "interdisciplinary"],
        "description": "A beautiful gardening project emphasizing empathy and restorative justice. Very aligned with the persona.",
        "background": "PureHeart is a non-profit foundation."
    }
    with open("proposals/P008.json", "w") as f:
        json.dump(backup, f, indent=4)

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
