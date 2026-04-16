import os

def build_env():
    base_dir = "assets/data_381"
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Create the bluetooth scan log
    log_content = """[10:23:01] Scan started...
[10:23:01] Device found: 00:1A:7D:DA:71:11 - Unknown
[10:23:02] Device found: 4C:34:88:9B:FF:22 - Smart_TV_LivingRoom
[10:23:04] Device found: A1:B2:C3:D4:E5:F6 - Aura_Hear_X9
[10:23:06] Device found: F4:0F:24:1A:B8:93 - Galaxy_S21
[10:23:08] Scan finished.
"""
    with open(os.path.join(base_dir, "bt_scan.log"), "w") as f:
        f.write(log_content)

    # 2. Create the buggy python script
    script_content = """import sys

def generate_token(mac_address):
    # MAC format: XX:XX:XX:XX:XX:XX
    parts = mac_address.strip().split(':')
    if len(parts) != 6:
        raise ValueError("Invalid MAC address format")
    
    # Sum the hex values
    total = sum([int(p, 16) for p in parts])
    
    # Multiply by 1337 and XOR with 0xABCD
    # I tinkered with this last night, but it keeps failing...
    token = (total * 1337) ^ "0xABCD"
    
    return hex(token)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_token.py <MAC_ADDRESS>")
        sys.exit(1)
    
    mac = sys.argv[1]
    print(generate_token(mac))
"""
    with open(os.path.join(base_dir, "generate_token.py"), "w") as f:
        f.write(script_content)

if __name__ == "__main__":
    build_env()
