import sys
import json

def convert(amount, date):
    # Mock logic: On 2023-10-15, 1 AC = 1.2 USD
    if date == "2023-10-15":
        rate = 1.2
        return json.dumps({"usd_equivalent": amount * rate, "rate": rate})
    return json.dumps({"error": "Exchange rate not found for this date."})

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Missing params"}))
    else:
        print(convert(float(sys.argv[1]), sys.argv[2]))
