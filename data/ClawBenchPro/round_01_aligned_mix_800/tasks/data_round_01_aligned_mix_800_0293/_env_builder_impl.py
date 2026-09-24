import os
import json

def build_env():
    # Define directories
    manifests_dir = "manifests"
    os.makedirs(manifests_dir, exist_ok=True)
    
    # Data definitions
    # Note: Logic for Problems:
    # 1. Weight > 50.0 (Some need decoding)
    # 2. Zip is not 5 digits
    # 3. Zip is 5 digits but 'Discontinued' in validator
    
    # route_alpha.dat (Simulated binary/text mix)
    # PKG-1001: 15.2 lbs, 90210 (Valid)
    # PKG-1002: 0x3F (Hex for 63.0), 90210 (Overweight)
    # PKG-1003: 5.0 lbs, 9021 (Invalid Zip Length)
    alpha_content = "ID:PKG-1001|W:15.2|Z:90210\nID:PKG-1002|W:0x3F|Z:90210\nID:PKG-1003|W:5.0|Z:9021"
    with open(os.path.join(manifests_dir, "route_alpha.dat"), "w") as f:
        f.write(alpha_content)

    # route_beta.pdf (Text-based simulation of a PDF dump)
    # PKG-2001: 48.9 lbs, 90210 (Valid)
    # PKG-2002: 60.5 lbs, 80000 (Overweight)
    # PKG-2003: 2.1 lbs, 99999 (Valid format, but Discontinued in Skill)
    beta_content = """
    --------------------------------------------
    PACKAGE MANIFEST REPORT - ROUTE BETA
    --------------------------------------------
    PKG-2001 | WEIGHT: 48.9 LBS | ZIP: 90210
    PKG-2002 | WEIGHT: 60.5 LBS | ZIP: 80000
    PKG-2003 | WEIGHT: 2.1 LBS  | ZIP: 99999
    --------------------------------------------
    """
    with open(os.path.join(manifests_dir, "route_beta.pdf"), "w") as f:
        f.write(beta_content)
        
    # route_gamma.log
    # PKG-3001: 10.0 lbs, 33101 (Valid)
    # PKG-3002: 0x33 (Hex for 51.0), 33101 (Overweight)
    # PKG-3003: 50.0 lbs, 90210 (Valid - exactly 50 is fine)
    gamma_content = "LOG_ENTRY: PKG-3001;W:10.0;Z:33101\nLOG_ENTRY: PKG-3002;W:0x33;Z:33101\nLOG_ENTRY: PKG-3003;W:50.0;Z:90210"
    with open(os.path.join(manifests_dir, "route_gamma.log"), "w") as f:
        f.write(gamma_content)

if __name__ == "__main__":
    build_env()
