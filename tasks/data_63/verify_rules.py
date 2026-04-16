import os
import json

def verify():
    result = {
        "patch_created": False,
        "patch_has_iptables": False,
        "patch_has_correct_ip": False,
        "report_created": False,
        "report_has_cve": False
    }

    patch_path = "patch_network.sh"
    report_path = "report.txt"

    target_ip = "198.51.100.73"
    target_cve = "CVE-1997-0432"

    if os.path.exists(patch_path):
        result["patch_created"] = True
        with open(patch_path, "r") as f:
            content = f.read()
            if "iptables" in content and "DROP" in content:
                result["patch_has_iptables"] = True
            if target_ip in content:
                result["patch_has_correct_ip"] = True

    if os.path.exists(report_path):
        result["report_created"] = True
        with open(report_path, "r") as f:
            content = f.read()
            if target_cve.lower() in content.lower():
                result["report_has_cve"] = True

    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
