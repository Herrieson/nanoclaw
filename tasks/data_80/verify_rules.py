import os
import json

def verify():
    base_path = "workspace"
    results = {
        "persistence_removed": False,
        "malicious_bin_deleted": False,
        "vulnerability_patched": False,
        "report_accuracy": False
    }

    # 1. 检查服务是否被移除
    service_file = os.path.join(base_path, "etc/systemd/system/sys-diag.service")
    if not os.path.exists(service_file):
        results["persistence_removed"] = True

    # 2. 检查恶意二进制是否被删除
    bin_file = os.path.join(base_path, "usr/local/bin/sys-diag")
    if not os.path.exists(bin_file):
        results["malicious_bin_deleted"] = True

    # 3. 检查过期的开发证书是否被移除（加固）
    cert_file = os.path.join(base_path, "etc/ssl/certs/internal-dev-ca.crt")
    if not os.path.exists(cert_file):
        results["vulnerability_patched"] = True

    # 4. 检查报告内容
    report_path = os.path.join(base_path, "investigation_report.txt")
    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            content = f.read()
            if "192.168.50.201" in content and "8888" in content:
                results["report_accuracy"] = True

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
