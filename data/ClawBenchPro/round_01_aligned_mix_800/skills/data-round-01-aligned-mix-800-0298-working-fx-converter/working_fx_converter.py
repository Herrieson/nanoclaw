import sys

def convert(amount, from_curr, to_curr):
    rate = 1.10
    if from_curr == "EUR" and to_curr == "USD":
        return float(amount) * rate
    return float(amount) # Simplified

if __name__ == "__main__":
    if len(sys.argv) > 3:
        print(convert(sys.argv[1], sys.argv[2], sys.argv[3]))
