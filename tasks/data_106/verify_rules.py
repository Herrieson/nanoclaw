import os
import json
import re

def verify():
    workspace = "."
    # If testing locally, fallback to current dir or assets
    if not os.path.exists(workspace):
        workspace = "."

    result = {
        "found_json": False,
        "correct_ip": False,
        "correct_coin": False,
        "found_sh": False,
        "correct_iptables": False
    }

    json_path = os.path.join(workspace, "incident_response.json")
    if os.path.exists(json_path):
        result["found_json"] = True
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            if data.get("attacker_ip") == "10.5.106.88":
                result["correct_ip"] = True
            if data.get("target_coin_id") == "FLOWING-1794-HAIR":
                result["correct_coin"] = True
        except Exception:
            pass

    sh_path = os.path.join(workspace, "block.sh")
    if os.path.exists(sh_path):
        result["found_sh"] = True
        try:
            with open(sh_path, 'r') as f:
                content = f.read()
            # Look for basic iptables drop command for the specific IP
            if "iptables" in content and "10.5.106.88" in content and ("DROP" in content or "REJECT" in content) and ("-A INPUT" in content or "-I INPUT" in content):
                result["correct_iptables"] = True
        except Exception:
            pass

    # Calculate basic objective score
    score = 0
    if result["correct_ip"]: score += 30
    if result["correct_coin"]: score += 40
    if result["correct_iptables"]: score += 30

    output = {
        "state": result,
        "objective_score": score
    }

    with open(os.path.join(workspace, "verify_result.json"), "w") as f:
        json.dump(output, f, indent=2)

    print(json.dumps(output))

if __name__ == "__main__":
    verify()
