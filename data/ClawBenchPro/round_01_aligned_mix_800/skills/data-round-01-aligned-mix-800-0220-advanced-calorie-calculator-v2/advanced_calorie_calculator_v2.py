import sys

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 advanced_calorie_calculator_v2.py <avg_hr> <duration_mins>")
        sys.exit(1)
    
    try:
        hr = float(sys.argv[1])
        duration = float(sys.argv[2])
        # Proprietary formula v2
        calories = int((hr - 50) * duration * 0.18)
        print(f"{calories}")
    except ValueError:
        print("Error: Inputs must be numbers.")
        sys.exit(1)

if __name__ == "__main__":
    main()
