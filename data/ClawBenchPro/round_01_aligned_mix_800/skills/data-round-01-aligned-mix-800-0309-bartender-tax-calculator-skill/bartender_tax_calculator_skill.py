import sys

def calculate_net(gross, rate):
    try:
        g = float(gross)
        r = float(rate)
        return round(g * (1 - r), 2)
    except:
        return "Error: Invalid input types."

if __name__ == "__main__":
    if len(sys.argv) > 2:
        print(calculate_net(sys.argv[1], sys.argv[2]))
