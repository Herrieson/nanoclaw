import os
import json
import random

def build_env():
    base_dir = "assets/data_359"
    claims_dir = os.path.join(base_dir, "claims")
    os.makedirs(claims_dir, exist_ok=True)

    habitats = {
        "Woodpecker": ["87501", "87502", "87505"],
        "Wild Turkey": ["87102", "87505", "87108"]
    }

    with open(os.path.join(base_dir, "nm_bird_habitats.json"), "w") as f:
        json.dump(habitats, f, indent=4)

    # 5 Valid Claims that meet all criteria
    valid_claims = [
        {"id": "NM-2023-011", "date": "2023-04-12", "zip": "87501", "amt": "1200.50", "desc": "Property damage due to Woodpecker pecking holes in cedar siding."},
        {"id": "NM-2023-025", "date": "2023-05-01", "zip": "87102", "amt": "850.25", "desc": "Client reports a Wild Turkey scratched the hood of their parked car."},
        {"id": "NM-2023-038", "date": "2023-05-15", "zip": "87502", "amt": "2150.00", "desc": "Woodpecker destroyed the exterior insulation. Heavy damage."},
        {"id": "NM-2023-042", "date": "2023-06-10", "zip": "87505", "amt": "330.25", "desc": "Aggressive wild turkey broke front porch window."},
        {"id": "NM-2023-049", "date": "2023-06-22", "zip": "87505", "amt": "110.00", "desc": "Woodpecker damage to roof eaves."}
    ]

    # Invalid Claims (Wrong zip for the bird, or different animals, or weather)
    invalid_claims = [
        {"id": "NM-2023-002", "date": "2023-04-13", "zip": "87109", "amt": "400.00", "desc": "Woodpecker pecked the garage door."}, # Invalid Zip
        {"id": "NM-2023-005", "date": "2023-04-14", "zip": "87501", "amt": "550.00", "desc": "Wild turkey dented the fender."}, # Invalid Zip
        {"id": "NM-2023-008", "date": "2023-04-18", "zip": "87501", "amt": "4500.00", "desc": "Hail damage to roof and solar panels."},
        {"id": "NM-2023-014", "date": "2023-04-20", "zip": "87505", "amt": "3000.00", "desc": "Black bear broke into the cabin."},
        {"id": "NM-2023-019", "date": "2023-04-25", "zip": "87108", "amt": "150.00", "desc": "Deer ate the landscaping and damaged sprinklers."},
        {"id": "NM-2023-022", "date": "2023-04-28", "zip": "87502", "amt": "700.00", "desc": "Wind storm blew away patio furniture."},
        {"id": "NM-2023-031", "date": "2023-05-08", "zip": "87102", "amt": "900.00", "desc": "Water pipe burst in the kitchen."}
    ]

    # Generate additional filler claims to make the parsing task realistic
    for i in range(50, 80):
        invalid_claims.append({
            "id": f"NM-2023-0{i}",
            "date": f"2023-07-{random.randint(10, 28)}",
            "zip": random.choice(["87501", "87102", "87505", "87109", "87502", "87108"]),
            "amt": f"{random.uniform(100, 5000):.2f}",
            "desc": random.choice([
                "Routine fender bender in parking lot.",
                "Wind shield cracked by flying debris.",
                "Roof leak after heavy monsoon rain.",
                "Vandalism to the mailbox.",
                "Tree branch fell on the tool shed."
            ])
        })

    all_claims = valid_claims + invalid_claims
    random.seed(42)
    random.shuffle(all_claims)

    formats = [
        "Claim #: {id} | Date: {date} | Location: {zip} | Cause: {desc} | Payout: ${amt}",
        "ID: {id}, Filed: {date}, Zip: {zip}. Description: {desc} Approved for ${amt}.",
        "=== CLAIM REPORT ===\nID: {id}\nDATE: {date}\nZIPCODE: {zip}\nAMOUNT: ${amt}\nNOTES: {desc}\n===================="
    ]

    for i, claim in enumerate(all_claims):
        fmt = random.choice(formats)
        content = fmt.format(**claim)
        with open(os.path.join(claims_dir, f"claim_log_{i:03d}.txt"), "w") as f:
            f.write(content)

if __name__ == "__main__":
    build_env()
