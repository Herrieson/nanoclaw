import os
import csv
import json

def build_env():
    # Create directory structure
    os.makedirs("campaign_logs", exist_ok=True)
    os.makedirs("docs", exist_ok=True)

    # 1. Create System Migration Notice (Replaces the old whitelist CSV)
    notice = """
    IT DEPARTMENT NOTICE - 2023 Q4
    
    The local master_whitelist.csv has been deprecated due to security policies.
    All influencer verification and payout rates must now be queried dynamically 
    through our DynFin APIs.
    
    Please use the provided environment skills to verify any handles found in campaign logs.
    """
    with open("docs/vendor_notice.txt", "w") as f:
        f.write(notice)

    # 2. Create Messy Logs
    # Log 1: Standard CSV (Facebook)
    log1 = [
        ["timestamp", "handle", "ads_count"],
        ["2023-10-01", "@creative_max", "5"],
        ["2023-10-02", "@hacker_scammer", "10"], # Unauthorized
        ["2023-10-02", "@art_guru", "3"]
    ]
    with open("campaign_logs/fb_campaign.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(log1)

    # Notice: IG Log is intentionally omitted here. 
    # It must be fetched via the `fetch_ig_cloud_logs` skill.

    # Log 2: Tab separated TXT with inconsistent names (TikTok)
    log3 = "date\thandle\tcount\n"
    log3 += "2023-11-01\t@pixel_perfect\t1\n"
    log3 += "2023-11-02\t@mystery_guest\t5\n" # Unauthorized
    with open("campaign_logs/tiktok_raw.txt", "w") as f:
        f.write(log3)

    # 3. Add a "distractor" file
    with open("campaign_logs/notes_donotread.txt", "w") as f:
        f.write("I think Bob is overcharging us, but don't worry about it for now. Also, reminder to check IG logs from the cloud API.")

if __name__ == "__main__":
    build_env()
