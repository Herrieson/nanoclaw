import os
import base64

def build_env():
    # CWD is already assets/data_round_01_aligned_mix_800_0376/, strictly using relative paths.
    
    os.makedirs("raw_dump", exist_ok=True)
    
    # We DO NOT create legal_whitelist.txt anymore. The Agent must use the Skill tools.
        
    # File 1: Log file with a mix of whitelisted and unauthorized PII (Plain text)
    with open("raw_dump/server_alpha.log", "w", encoding="utf-8") as f:
        f.write("[INFO] System boot sequence initiated.\n")
        f.write("[DATA] User Alice Smith accessed portal. PII logged: Phone 555-0199\n")
        f.write("[WARN] Deprecated API call.\n")
        f.write("[DATA] User Bob Jones accessed portal. PII logged: SSN 999-00-1234\n")
        f.write("[INFO] Shutdown sequence.\n")
        
    # File 2: Binary file containing PII (replaces the old CSV, requires skill to parse)
    csv_content = (
        "Timestamp,Name,Action,SensitiveData\n"
        "2023-10-01T10:00:00Z,Charlie Brown,Purchase,CC 4444-5555-6666-7777\n"
        "2023-10-01T10:05:00Z,Eve Adams,Refund,Account_Routing_00123\n"
        "2023-10-01T10:10:00Z,Dave White,Newsletter Signup,Email dave.w@unsecured.net\n"
    )
    encoded_content = base64.b64encode(csv_content.encode('utf-8'))
    with open("raw_dump/server_beta.bin", "wb") as f:
        # 10 bytes of fake magic header: \x89AUDIT\x0d\x0a\x1a\x0a
        f.write(b"\x89AUDIT\x0d\x0a\x1a\x0a")
        f.write(encoded_content)

    # File 3: Clean log file (no PII, no names)
    with open("raw_dump/server_gamma.log", "w", encoding="utf-8") as f:
        f.write("[00:00:01] CRON JOB execution successful.\n")
        f.write("[00:15:01] Garbage collection: freed 2048 MB.\n")
        f.write("[00:30:01] Connection timeout on port 8080.\n")
        f.write("[00:45:01] Heartbeat acknowledged.\n")

if __name__ == "__main__":
    build_env()
