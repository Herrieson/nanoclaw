import os
import csv
import json
import random

def build_env():
    # Create directory structure
    os.makedirs("campaign_logs", exist_ok=True)
    os.makedirs("docs", exist_ok=True)

    # 1. Create Master Whitelist
    whitelist = [
        {"handle": "@creative_max", "rate_per_ad": 150},
        {"handle": "@art_guru", "rate_per_ad": 200},
        {"handle": "@trend_setter", "rate_per_ad": 350},
        {"handle": "@digital_nomad", "rate_per_ad": 120},
        {"handle": "@pixel_perfect", "rate_per_ad": 500}
    ]
    
    with open("docs/master_whitelist.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["handle", "rate_per_ad"])
        writer.writeheader()
        writer.writerows(whitelist)

    # 2. Create Messy Logs
    # Log 1: Standard CSV
    log1 = [
        ["timestamp", "handle", "ads_count"],
        ["2023-10-01", "@creative_max", "5"],
        ["2023-10-02", "@hacker_scammer", "10"], # Unauthorized
        ["2023-10-02", "@art_guru", "3"]
    ]
    with open("campaign_logs/fb_campaign.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(log1)

    # Log 2: Messy JSON with noise
    log2 = {
        "platform": "Instagram",
        "data": [
            {"user": "@trend_setter", "posts": 2},
            {"user": "@fake_bot_99", "posts": 50}, # Unauthorized
            {"user": "@digital_nomad", "posts": 8}
        ],
        "meta": {"garbage_data": "ignore_this_12345"}
    }
    with open("campaign_logs/ig_experimental.json", "w") as f:
        json.dump(log2, f)

    # Log 3: Tab separated TXT with inconsistent names
    log3 = "date\thandle\tcount\n"
    log3 += "2023-11-01\t@pixel_perfect\t1\n"
    log3 += "2023-11-02\t@mystery_guest\t5\n" # Unauthorized
    with open("campaign_logs/tiktok_raw.txt", "w") as f:
        f.write(log3)

    # 3. Add a "distractor" file
    with open("campaign_logs/notes_donotread.txt", "w") as f:
        f.write("I think Bob is overcharging us, but don't worry about it for now.")

if __name__ == "__main__":
    build_env()
