import os

def build_env():
    os.makedirs("logs", exist_ok=True)
    os.makedirs("docs", exist_ok=True)
    os.makedirs("investigation", exist_ok=True)

    with open("docs/approved_staff.txt", "w") as f:
        f.write("Alice\nBob\nCharlie\nDave\n")

    log_data = [
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
    with open("logs/access_events.log", "w") as f:
        f.writelines(log_data)

if __name__ == "__main__":
    build_env()
