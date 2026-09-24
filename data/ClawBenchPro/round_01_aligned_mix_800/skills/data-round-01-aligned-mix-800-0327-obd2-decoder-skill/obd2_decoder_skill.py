import sys

def decode(hex_code):
    mapping = {
        "0xA1": "P0113 (Intake Air Temperature Sensor 1 Circuit High)",
        "0xB2": "P0300 (Random/Multiple Cylinder Misfire Detected)",
        "0xC3": "P0101 (Mass or Volume Air Flow Sensor A Circuit Range/Performance)",
        "0xD4": "P0442 (Evaporative Emission System Leak Detected)",
        "0xE5": "P0420 (Catalyst System Efficiency Below Threshold)",
        "0xF6": "P0302 (Cylinder 2 Misfire Detected)"
    }
    hex_clean = hex_code.strip()
    return mapping.get(hex_clean, f"Unknown FaultID: {hex_clean}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python obd2_decoder_skill.py <hex_code>")
        sys.exit(1)
    print(decode(sys.argv[1]))
