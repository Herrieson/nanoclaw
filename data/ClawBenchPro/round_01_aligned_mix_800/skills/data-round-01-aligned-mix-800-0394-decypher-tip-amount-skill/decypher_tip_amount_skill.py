import sys
import re

def decypher(text):
    # Extract numbers from the CRYPT_xxx_X format
    match = re.search(r"CRYPT_(\d+)_X", text)
    if match:
        return match.group(1)
    return "Error: Invalid Format"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(decypher(sys.argv[1]))
