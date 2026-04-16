import os
import csv
import json

def build_env():
    base_dir = "assets/data_447"
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(os.path.join(base_dir, "maintenance_logs"), exist_ok=True)

    # 1. Generate tenant_registry.csv
    registry_path = os.path.join(base_dir, "tenant_registry.csv")
    tenants = [
        {"Unit": "101", "Tenant Name": "John Doe", "Lease Start": "2021-04-01", "Pet Deposit Paid": "No"},
        {"Unit": "102", "Tenant Name": "Jane Smith", "Lease Start": "2020-08-15", "Pet Deposit Paid": "Yes"},
        {"Unit": "103", "Tenant Name": "Bob Johnson", "Lease Start": "2022-01-10", "Pet Deposit Paid": "No"},
        {"Unit": "104", "Tenant Name": "Alice Brown", "Lease Start": "2023-05-20", "Pet Deposit Paid": "No"},
        {"Unit": "105", "Tenant Name": "Charlie Davis", "Lease Start": "2019-11-01", "Pet Deposit Paid": "Yes"},
        {"Unit": "106", "Tenant Name": "Eva Green", "Lease Start": "2022-09-01", "Pet Deposit Paid": "No"},
        {"Unit": "107", "Tenant Name": "Michael Scott", "Lease Start": "2021-03-15", "Pet Deposit Paid": "Yes"},
    ]
    with open(registry_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Unit", "Tenant Name", "Lease Start", "Pet Deposit Paid"])
        writer.writeheader()
        writer.writerows(tenants)

    # 2. Generate maintenance logs
    logs = {
        "log_101_Oct.txt": "Replaced HVAC filter. Note: Tenant's golden retriever was very loud and aggressive during the visit.",
        "log_102_Oct.txt": "Fixed master bedroom window lock. Friendly tabby cat kept trying to escape.",
        "log_103_Oct.txt": "Routine fire alarm inspection. All clear. No issues found.",
        "log_105_Oct.txt": "Unclogged kitchen sink. Normal wear and tear.",
        "log_106_Oct.txt": "Emergency plumbing call. Master bathroom toilet was completely clogged. Found large amounts of 'flushable' cat litter in the pipes. Advised tenant to use the trash.",
        "log_107_Oct.txt": "Repaired drywall damage in hallway. Looks like dog chew marks on the baseboards."
    }
    for filename, content in logs.items():
        with open(os.path.join(base_dir, "maintenance_logs", filename), 'w') as f:
            f.write(content)

    # 3. Generate complaints.json
    complaints = [
        {
            "date": "2023-10-12",
            "complainant_unit": "103",
            "offending_unit": "104",
            "issue": "Noise complaint. The parrot in 104 squawks incessantly from 5 AM until noon. It is driving me crazy."
        },
        {
            "date": "2023-10-15",
            "complainant_unit": "105",
            "offending_unit": "101",
            "issue": "Dog barking all night long. Please do something."
        },
        {
            "date": "2023-10-18",
            "complainant_unit": "106",
            "offending_unit": "107",
            "issue": "Smell of cigarette smoke coming through the vents."
        }
    ]
    with open(os.path.join(base_dir, "complaints.json"), 'w') as f:
        json.dump(complaints, f, indent=4)

if __name__ == "__main__":
    build_env()
