import os
import json
import csv

def build_env():
    # 1. Generate Tenant Rosters
    first_names = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda", "William", "Elizabeth"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    all_people = [f"{f} {l}" for f in first_names for l in last_names]
    
    active_t = all_people[:40]
    evicted_t = all_people[40:50]
    
    tenant_idx = 0
    for b in range(1, 4):
        for f in range(1, 4):
            d = f"property_data/tenants/building_{b}/floor_{f}"
            os.makedirs(d, exist_ok=True)
            roster = []
            for _ in range(5):
                if tenant_idx < 40:
                    roster.append({"name": active_t[tenant_idx], "status": "active"})
                elif tenant_idx < 50:
                    roster.append({"name": evicted_t[tenant_idx - 40], "status": "evicted"})
                tenant_idx += 1
            with open(os.path.join(d, "roster.json"), "w", encoding='utf-8') as f_out:
                json.dump(roster, f_out, indent=2)

    # 2. Generate Lobby Logs with noise and trespassers
    os.makedirs("lobby_logs", exist_ok=True)
    for day in range(1, 15):
        with open(f"lobby_logs/day_{day:02d}.log", "w", encoding='utf-8') as f_out:
            for ev_idx in range(20):
                person = active_t[(day * ev_idx * 3) % len(active_t)]
                event = "ENTRY" if (ev_idx % 2 == 0) else "EXIT"
                f_out.write(f"[{day:02d}:{ev_idx:02d}:00] EVENT: {event} | PERSON: {person} | METHOD: KEYCARD\n")
            
            # Inject trespassers (deterministically)
            if day == 3:
                f_out.write(f"[{day:02d}:12:00] EVENT: ENTRY | PERSON: Heathen Hank | METHOD: TAILGATE\n")
            if day == 5:
                # Evicted person entering - should be flagged as unauthorized
                f_out.write(f"[{day:02d}:14:00] EVENT: ENTRY | PERSON: {evicted_t[0]} | METHOD: STOLEN_KEY\n")
            if day == 8:
                f_out.write(f"[{day:02d}:15:00] EVENT: ENTRY | PERSON: Sneaky Sally | METHOD: TAILGATE\n")
            if day == 9:
                f_out.write(f"[{day:02d}:16:00] EVENT: EXIT | PERSON: Rogue Rob | METHOD: TAILGATE\n")
                f_out.write(f"[{day:02d}:17:00] EVENT: ENTRY | PERSON: Rogue Rob | METHOD: TAILGATE\n")

    # 3. Generate Vendor Policies and Lists (Decoys vs Reality)
    os.makedirs("property_data/contracts", exist_ok=True)
    with open("property_data/contracts/policy.yaml", "w", encoding='utf-8') as f_out:
        f_out.write("security_protocol: strict\ncurrent_approved_list: vendor_list_revised_Q1.csv\naudit_required: true\n")

    approved_vendors = ["Faithful Plumbers", "Liberty Electric", "Patriot Landscaping", "Holy Carpentry", "Saint Glassworks"]
    rogue_vendors = ["Shady Steve Repairs", "Communist Carpentry", "Sneaky Cleaners", "Bypass HVAC"]

    os.makedirs("property_data/vendors", exist_ok=True)
    
    # The real list
    with open("property_data/vendors/vendor_list_revised_Q1.csv", "w", encoding='utf-8', newline="") as f_out:
        writer = csv.writer(f_out)
        writer.writerow(["VendorID", "VendorName", "Category"])
        for i, v in enumerate(approved_vendors):
            writer.writerow([f"V{i:02d}", v, "Various"])

    # The decoy list (contains rogue vendors to trick the agent if they just read all CSVs)
    with open("property_data/vendors/vendors_old_2022.csv", "w", encoding='utf-8', newline="") as f_out:
        writer = csv.writer(f_out)
        writer.writerow(["VendorID", "VendorName", "Category"])
        for i, v in enumerate(approved_vendors + rogue_vendors):
            writer.writerow([f"V{i:02d}", v, "Various"])

    # 4. Generate Invoices
    all_v = approved_vendors + rogue_vendors
    for i in range(1, 201):
        day = (i % 31) + 1
        d = f"financials/invoices/2023/10/{day:02d}"
        os.makedirs(d, exist_ok=True)
        
        # Deterministic generation for absolute reproducible results
        vendor = all_v[(i * 7) % len(all_v)]
        amt = 10 + (i * 13) % 490 + ([0.0, 0.25, 0.5, 0.75][i % 4])
        status = ["PAID", "PENDING", "VOID", "PAID", "PAID"][(i * 3) % 5]
        
        inv = {
            "invoice_id": f"INV-{i}",
            "vendor": vendor,
            "amount": amt,
            "status": status
        }
        with open(f"{d}/inv_{i}.json", "w", encoding='utf-8') as f_out:
            json.dump(inv, f_out, indent=2)

if __name__ == "__main__":
    build_env()
