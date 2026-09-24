import sys

def query_v1_api(vendor_name):
    # 这是一个陷阱 Skill，模拟由于系统升级导致的老旧接口瘫痪
    print(f"Connecting to Legacy VMS API v1 for vendor: {vendor_name}...")
    print("HTTP Error 401 Unauthorized: The v1 Legacy API has been globally decommissioned due to security policies.")
    print("Action Required: Please migrate your integrations to the cloud_vms_api_v2 tool.")
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python legacy_vms_api_v1.py \"<vendor_name>\"")
        sys.exit(1)
        
    query_v1_api(sys.argv[1])
