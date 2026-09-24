import sys

def convert_mv_to_ph(mv_value):
    try:
        mv = float(mv_value)
        # Nernst-inspired mock calibration equation for this specific sensor
        ph = 7.0 - (mv / 50.0)
        return round(ph, 2)
    except ValueError:
        return "Error: Invalid mV value. Please provide a numeric argument."

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python isfet_mv_to_ph_skill.py <mV_reading>")
    else:
        result = convert_mv_to_ph(sys.argv[1])
        print(f"Converted pH Value: {result}")
