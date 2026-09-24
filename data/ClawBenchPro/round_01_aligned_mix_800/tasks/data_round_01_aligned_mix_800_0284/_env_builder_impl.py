import os

def build_env():
    # Create directory structure
    os.makedirs("raw_logs", exist_ok=True)
    
    # Writing the raw trail reports (Hazard levels are REMOVED, Agent must use Skill)
    # Using Terrain Codes to force tool usage
    with open("raw_logs/trail_reports.txt", "w", encoding="utf-8") as f:
        f.write("Log 101: Pine Ridge | Code: PR-01 | Status: Minor overgrowth\n")
        f.write("Log 102: Bear Creek | Code: BC-05 | Status: Massive fallen oak\n")
        f.write("Log 103: Summit Path | Code: SP-04 | Status: Dangerous washout\n")
        f.write("Log 104: Lake Loop | Code: LL-01 | Status: Completely clear\n")
        f.write("Log 105: Canyon Descent | Code: CD-06 | Status: Rockslide near edge\n")
        f.write("Log 106: Meadow Trail | Code: MT-03 | Status: Muddy\n")

    # Create a dummy "database" file that cannot be read as text
    with open("raw_logs/volunteers.db", "wb") as f:
        # Mock binary content to force use of legacy_db_extractor
        f.write(b"\x53\x51\x4c\x69\x74\x65\x20\x66\x6f\x72\x6d\x61\x74\x20\x33\x00")
        f.write(b"DATA_ENCRYPTED_STREAM_VOLUNTEER_ROSTER_V1.0")

if __name__ == "__main__":
    build_env()
