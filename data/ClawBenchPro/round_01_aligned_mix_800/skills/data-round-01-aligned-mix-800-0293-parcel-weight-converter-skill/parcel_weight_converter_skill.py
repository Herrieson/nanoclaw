import sys

def convert_weight(weight_str):
    try:
        if weight_str.startswith("0x"):
            return float(int(weight_str, 16))
        return float(weight_str)
    except:
        return "Error: Unsupported weight format."

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(convert_weight(sys.argv[1]))
