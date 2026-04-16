import os
import json
import random

def build_env():
    base_dir = "assets/data_479"
    os.makedirs(base_dir, exist_ok=True)
    
    # Generate messy log file
    log_content = """
[DEBUG] Initializing campaign tracker...
[WARN] Connection timeout. Retrying.
[INFO] Fetched influencer data chunk 1.
GARBAGE DATA {x: 1, y: 2} >> error
[CONTACT_RECORD] Handle: @artsy_fartsy | Name: Sarah J. | BaseRate: 250
[DEBUG] Checking rate limits.
[CONTACT_RECORD] Handle: @austin_vibes | Name: Mark | BaseRate: 400
[ERROR] Failed to load image for @austin_vibes
[CONTACT_RECORD] Handle: @culture_hound | Name: Elena | BaseRate: 150
[INFO] Refreshing token...
random string of text that means nothing
[CONTACT_RECORD] Handle: @fest_junkie | Name: Tom | BaseRate: 300
[WARN] Deprecated API call used.
[CONTACT_RECORD] Handle: @indy_music_atx | Name: Greg | BaseRate: 500
[DEBUG] System shutdown initiated.
    """
    
    with open(os.path.join(base_dir, "influencers_raw.log"), "w") as f:
        f.write(log_content.strip())
        
    # Generate social dump
    social_dir = os.path.join(base_dir, "social_dump")
    os.makedirs(social_dir, exist_ok=True)
    
    influencers = {
        "@artsy_fartsy": {"followers": 12000, "engagement_score": 45, "platform": "Instagram"},
        "@austin_vibes": {"followers": 45000, "engagement_score": 112, "platform": "TikTok"},
        "@culture_hound": {"followers": 8000, "engagement_score": 20, "platform": "Twitter"},
        "@fest_junkie": {"followers": 22000, "engagement_score": 68, "platform": "Instagram"},
        "@indy_music_atx": {"followers": 55000, "engagement_score": 150, "platform": "TikTok"},
        # Add some noise
        "@random_guy": {"followers": 100, "engagement_score": 1, "platform": "Twitter"}
    }
    
    for handle, data in influencers.items():
        with open(os.path.join(social_dir, f"{handle.replace('@', '')}_profile.json"), "w") as f:
            json.dump(data, f, indent=4)

if __name__ == "__main__":
    build_env()
