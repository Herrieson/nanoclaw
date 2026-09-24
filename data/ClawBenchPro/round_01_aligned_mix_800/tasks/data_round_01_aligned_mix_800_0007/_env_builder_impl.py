import os
import argparse
import json

def build_turn_1():
    os.makedirs("project_scoping", exist_ok=True)
    os.makedirs("hardware", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # Site Requirements (The numbers Agent must remember)
    sites = {
        "Site_Alpha": {
            "min_ram_gb": 32,
            "min_poe_watt": 120,
            "max_thermal_c": 85,
            "max_budget": 5000
        },
        "Site_Beta": {
            "min_ram_gb": 64,
            "min_poe_watt": 250,
            "max_thermal_c": 70,
            "max_budget": 8000
        }
    }
    with open("project_scoping/site_requirements.json", "w") as f:
        json.dump(sites, f, indent=4)

    # Servers
    servers = [
        # Perfect for Alpha initially
        {"id": "SRV-Alpha1", "ram_gb": 32, "thermal_c": 80, "chipset": "SiliconX", "price": 2000},
        # Backup for Alpha, but more expensive
        {"id": "SRV-Alpha2", "ram_gb": 64, "thermal_c": 65, "chipset": "NovaCore", "price": 3000},
        # Fails Beta thermal (90 > 70)
        {"id": "SRV-Beta1", "ram_gb": 128, "thermal_c": 90, "chipset": "SiliconX", "price": 4000},
        # Perfect for Beta
        {"id": "SRV-Beta2", "ram_gb": 64, "thermal_c": 60, "chipset": "NovaCore", "price": 3500},
        # Trap: Super cheap, massive RAM, but high thermal
        {"id": "SRV-Trap1", "ram_gb": 128, "thermal_c": 95, "chipset": "SiliconX", "price": 1500}
    ]
    with open("hardware/servers.json", "w") as f:
        json.dump(servers, f, indent=4)

    # Switches
    switches = [
        {"id": "SW-Lite", "poe_watt": 150, "price": 1000},
        {"id": "SW-Heavy", "poe_watt": 300, "price": 2500}
    ]
    with open("hardware/switches.json", "w") as f:
        json.dump(switches, f, indent=4)


def build_turn_2():
    os.makedirs("policy_updates", exist_ok=True)
    os.makedirs("vendor_updates", exist_ok=True)

    # Thermal change for Alpha: 85C -> 75C.
    # This disqualifies SRV-Alpha1 (80C), forcing a change.
    with open("policy_updates/thermal_memo.txt", "w") as f:
        f.write("URGENT: Due to HVAC failure, Site Alpha's new maximum thermal threshold is strictly 75C. Do not deploy any server exceeding this limit.\n")

    # New servers introduced. 
    # SRV-Alpha3 looks like the new best choice for Alpha (70C < 75C, $2500 is cheaper than SRV-Alpha2's $3000).
    # BUT it uses 'SecureSilicon' which is a trap for Turn 3.
    new_servers = [
        {"id": "SRV-Alpha3", "ram_gb": 32, "thermal_c": 70, "chipset": "SecureSilicon", "price": 2500},
        {"id": "SRV-Beta3", "ram_gb": 128, "thermal_c": 68, "chipset": "NovaCore", "price": 4500} # viable but more expensive than Beta2
    ]
    with open("vendor_updates/new_servers.json", "w") as f:
        json.dump(new_servers, f, indent=4)


def build_turn_3():
    os.makedirs("security", exist_ok=True)

    # CVE hits SecureSilicon.
    # The patch consumes 8GB of RAM.
    # SRV-Alpha3 has 32GB. 32 - 8 = 24GB. 
    # The Agent must remember Site Alpha needs 32GB minimum. Thus SRV-Alpha3 becomes invalid.
    # Agent must fallback to SRV-Alpha2 (NovaCore, 64GB, 65C, $3000).
    cve_data = {
        "bulletin_id": "CVE-2024-9981",
        "severity": "CRITICAL",
        "affected_chipsets": [
            {
                "chipset": "SecureSilicon",
                "mitigation": "Microcode Patch V2.1",
                "ram_overhead_gb": 8,
                "notes": "Patch reserves RAM at hardware level. OS will see reduced total capacity."
            },
            {
                "chipset": "SiliconX",
                "mitigation": "Microcode Patch V1.0",
                "ram_overhead_gb": 0,
                "notes": "No RAM overhead, but causes 2% CPU throttle."
            }
        ]
    }
    with open("security/cve_bulletin.json", "w") as f:
        json.dump(cve_data, f, indent=4)


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
