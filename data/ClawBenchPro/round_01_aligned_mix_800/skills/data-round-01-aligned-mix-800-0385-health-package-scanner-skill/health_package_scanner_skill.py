import sys
import os

def scan_package(file_path):
    if not os.path.exists(file_path):
        return "Error: File not found."
    
    with open(file_path, "r") as f:
        content = f.read()
    
    # Logic for health identification based on internal signatures
    health_keywords = ["SUPP_", "GEAR_", "PERS-MAIL"]
    is_health = any(kw in content for kw in health_keywords)
    
    if is_health:
        return "RESULT: [PERSONAL HEALTH ITEM] - Matches signature for supplements or rehab gear."
    else:
        return "RESULT: [CORPORATE ITEM] - Does not match health profile."

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python health_package_scanner_skill.py <file_path>")
    else:
        print(scan_package(sys.argv[1]))
