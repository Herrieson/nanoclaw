import sys
import json

def analyze_energy(wattage, insulation):
    try:
        w = float(wattage)
        i = float(insulation)
        # Professional logic: High wattage and poor insulation
        if w > 500 and i < 0.5:
            return json.dumps({"status": "High-Energy", "recommendation": "Solar Upgrade Highly Recommended"})
        else:
            return json.dumps({"status": "Low-Energy", "recommendation": "Standard Maintenance"})
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    if len(sys.argv) > 2:
        print(analyze_energy(sys.argv[1], sys.argv[2]))
