import json

def fetch_ig_cloud_logs():
    """
    Retrieves the cloud-stored Instagram experimental campaign logs.
    """
    log_data = {
        "platform": "Instagram",
        "data": [
            {"user": "@trend_setter", "posts": 2},
            {"user": "@fake_bot_99", "posts": 50}, 
            {"user": "@digital_nomad", "posts": 8}
        ],
        "meta": {"garbage_data": "ignore_this_cloud_noise_12345"}
    }
    return json.dumps(log_data, indent=2)
