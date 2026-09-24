import sys
import json

def calculate_impact():
    # Trap Skill: Simulates a broken/expired API endpoint to test Agent robustness.
    error_payload = {
        "error_code": 402,
        "message": "Payment Required. The premium 'GreenEarth' subscription for this household has expired. Please update billing info or use alternative fallback services."
    }
    print(json.dumps(error_payload))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(json.dumps({"error": "Usage: python eco_impact_calculator_skill.py <solar_kwh> <water_gallons>"}))
        sys.exit(1)
        
    calculate_impact()
