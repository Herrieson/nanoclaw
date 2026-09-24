import sys
import base64
import argparse
import json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="Path to the .bin file")
    args = parser.parse_args()

    if not args.file or not args.file.endswith(".bin"):
        print("Error: Please provide a valid .bin file path.")
        return

    try:
        with open(args.file, "rb") as f:
            data = f.read()
            decoded = base64.b64decode(data).decode('utf-8')
            print(decoded)
    except Exception as e:
        print(f"Error: Failed to decode ledger file. {str(e)}")

if __name__ == "__main__":
    main()
