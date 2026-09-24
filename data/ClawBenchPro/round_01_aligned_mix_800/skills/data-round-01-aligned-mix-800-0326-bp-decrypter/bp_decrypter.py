import sys
import argparse

def decode(hex_str):
    try:
        val = int(hex_str, 16)
        # Reverse the XOR encryption used by the sensor
        return str(val ^ 0xAA)
    except Exception as e:
        return f"Error: Invalid format. {e}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="Hex string to decode")
    args = parser.parse_args()
    print(decode(args.data))
