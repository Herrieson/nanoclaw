import os
import random
import csv
import json

def build_env():
    # 1. Setup directories
    directories = [
        "deliverables",
        "management_memos",
        "legacy_crm",
        "global_logistics",
        "email_dump/agent_alice/inbox",
        "email_dump/agent_alice/spam",
        "email_dump/agent_bob/inbox",
        "email_dump/system_archive/2023",
    ]
    for d in directories:
        os.makedirs(d, exist_ok=True)

    # 2. Create Management Memos (Policy definition)
    # The agent needs to find the one with 'CURRENT' or 'ACTIVE'
    memos = {
        "policy_v1_2021_obsolete.yaml": "refund_threshold_days: 7\nrequire_escalation: true\n",
        "draft_policy_proposed.txt": "Hey team, maybe we should change the delay threshold to 2 days? Let's discuss.\n",
        "Q3_POLICY_ACTIVE_FINAL.json": json.dumps({"policy_type": "refund", "refund_threshold_days": 3, "manager": "Karen"}),
        "holiday_guidelines.md": "# Holiday Rules\nNo refunds unless delayed by 10 days."
    }
    for filename, content in memos.items():
        with open(os.path.join("management_memos", filename), "w") as f:
            f.write(content)

    # Threshold for golden records
    policy_threshold = 3 

    # 3. Generate Data Pools
    # Golden Records (10 guaranteed correct chains)
    golden_records = []
    for i in range(10):
        golden_records.append({
            "ticket_ref": f"GOLD-REF-{i+100}",
            "order_id": f"ORD-GLD-{i+8000}",
            "customer_name": f"Golden VIP {i+1}",
            "email": f"vip{i+1}@gold.com",
            "delay": random.randint(policy_threshold + 1, policy_threshold + 5),
            "keyword": random.choice(["give me a refund", "money back please", "I demand a refund"]),
            "status": "UNRESOLVED"
        })

    # Noise Records (Large volume)
    noise_tickets = []
    noise_crm = []
    noise_logistics = []

    # Safe keywords that don't trigger the refund condition
    safe_complaints = [
        "Where is my package?", "This is taking too long.", "Can you check the status?", 
        "Tracking is stuck.", "Please update me.", "I am so disappointed.", 
        "When will it arrive?", "Terrible service."
    ]

    for i in range(1200):
        t_ref = f"TREF-{random.randint(10000, 99999)}-{i}"
        o_id = f"ORD-{random.randint(100000, 999999)}"
        c_name = f"User_{i}_Name"
        c_email = f"user_{i}@mail.com"
        
        # Decide if this ticket is resolved or unresolved
        is_unresolved = random.choice([True, False])
        t_status = "UNRESOLVED" if is_unresolved else "RESOLVED"
        
        # Ensure noise tickets DO NOT contain refund keywords if they are UNRESOLVED
        # If they are RESOLVED, they can contain refund keywords (as decoys)
        if t_status == "RESOLVED":
            msg = random.choice(safe_complaints + ["I want a refund", "money back"])
        else:
            msg = random.choice(safe_complaints) # STRICTLY NO REFUND KEYWORDS here to prevent false positives

        noise_tickets.append({
            "ticket_ref": t_ref,
            "status": t_status,
            "msg": msg
        })
        
        noise_crm.append([t_ref, o_id, c_name, c_email])
        
        # Generate varied delay days (some above threshold, some below)
        noise_logistics.append({"order_id": o_id, "delay": random.randint(0, 10)})

    # 4. Write CRM Database (Mix golden + noise)
    crm_path = os.path.join("legacy_crm", "customer_database.csv")
    with open(crm_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Ticket_Ref", "Order_ID", "Customer_Name", "Contact_Email"])
        # Add golden
        for g in golden_records:
            writer.writerow([g["ticket_ref"], g["order_id"], g["customer_name"], g["email"]])
        # Add noise
        writer.writerows(noise_crm)

    # 5. Write Global Logistics (Split into different formats/regions)
    na_csv_data = [["order_code", "region", "status", "delay_days"]]
    eu_json_data = []
    apac_txt_data = []

    all_logistics = [{"order_id": g["order_id"], "delay": g["delay"]} for g in golden_records] + noise_logistics
    random.shuffle(all_logistics)

    for idx, log in enumerate(all_logistics):
        if idx % 3 == 0:
            na_csv_data.append([log["order_id"], "NA", "IN_TRANSIT", log["delay"]])
        elif idx % 3 == 1:
            eu_json_data.append({"orderID": log["order_id"], "eu_status": "delayed", "delay_duration": log["delay"]})
        else:
            apac_txt_data.append(f"Order:{log['order_id']} | Stat:TRANSIT | DelayDays:{log['delay']}")

    with open(os.path.join("global_logistics", "na_region_logs.csv"), "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(na_csv_data)
        
    with open(os.path.join("global_logistics", "eu_region_logs.json"), "w", encoding="utf-8") as f:
        json.dump(eu_json_data, f)
        
    with open(os.path.join("global_logistics", "apac_region_logs.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(apac_txt_data))

    # 6. Write Shredded Email Dumps
    all_tickets = [{"ref": g["ticket_ref"], "status": g["status"], "msg": g["keyword"]} for g in golden_records]
    for n in noise_tickets:
        all_tickets.append({"ref": n["ticket_ref"], "status": n["status"], "msg": n["msg"]})
        
    random.shuffle(all_tickets)
    
    dump_folders = [
        "email_dump/agent_alice/inbox",
        "email_dump/agent_alice/spam",
        "email_dump/agent_bob/inbox",
        "email_dump/system_archive/2023"
    ]

    for idx, t in enumerate(all_tickets):
        folder = dump_folders[idx % len(dump_folders)]
        format_type = idx % 3
        
        if format_type == 0:
            # JSON format
            filepath = os.path.join(folder, f"ticket_frag_{idx}.json")
            with open(filepath, "w") as f:
                json.dump({"meta": {"ticket_reference": t["ref"], "state": t["status"]}, "body": t["msg"]}, f)
        elif format_type == 1:
            # TXT format
            filepath = os.path.join(folder, f"log_{idx}.txt")
            with open(filepath, "w") as f:
                f.write(f"---TICKET START---\nRefCode: {t['ref']}\nCurrentStatus: {t['status']}\n\nMessage:\n{t['msg']}\n---END---\n")
        else:
            # Fake log format
            filepath = os.path.join(folder, f"sys_export_{idx}.log")
            with open(filepath, "w") as f:
                f.write(f"ENTRY_ID: {idx} | TICKET_REF={t['ref']} | STATUS={t['status']} | CONTENT=\"{t['msg']}\"\n")

if __name__ == "__main__":
    build_env()
