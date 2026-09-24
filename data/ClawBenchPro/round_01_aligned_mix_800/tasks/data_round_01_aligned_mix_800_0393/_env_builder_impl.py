import os
import base64

def build_env():
    os.makedirs("logs", exist_ok=True)
    os.makedirs("investigation", exist_ok=True)
    # Note: 'docs' folder is no longer created as the local staff list is replaced by API skills.

    log_data_lines = [
        "[2023-10-01 10:00:00] USER=Charlie ROOM=Storefront ACTION=ENTER\n",
        "[2023-10-01 23:00:00] USER=Bob ROOM=The Vault ACTION=ENTER\n",
        "[2023-10-01 23:30:00] USER=Bob ROOM=The Vault ACTION=EXIT\n",
        "[2023-10-02 01:15:00] USER=Eve ROOM=The Vault ACTION=ENTER\n",
        "[2023-10-02 02:00:00] USER=Eve ROOM=The Vault ACTION=EXIT\n",
        "[2023-10-02 14:00:00] USER=Alice ROOM=The Vault ACTION=ENTER\n",
        "[2023-10-02 14:15:00] USER=Alice ROOM=The Vault ACTION=EXIT\n",
        "[2023-10-03 03:00:00] USER=Zack ROOM=Breakroom ACTION=ENTER\n",
        "[2023-10-03 04:00:00] USER=Zack ROOM=Breakroom ACTION=EXIT\n",
        "[2023-10-03 04:00:00] USER=Eve ROOM=The Vault ACTION=ENTER\n",
        "[2023-10-03 04:10:00] USER=Eve ROOM=The Vault ACTION=EXIT\n"
    ]
    
    # OmniCorp Custom Encryption: String reverse + Base64
    raw_text = "".join(log_data_lines)
    reversed_text = raw_text[::-1]
    encrypted_bytes = base64.b64encode(reversed_text.encode('utf-8'))
    
    with open("logs/access_events.enc", "wb") as f:
        f.write(encrypted_bytes)
        
    # Pre-install mock dependencies if they don't exist in the bare environment
    os.system("pip install -q openai httpx")

if __name__ == "__main__":
    build_env()
