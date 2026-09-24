import sys
import argparse
import time

def call_epc_api(hash_val):
    # Simulate a network attempt to a broken internal gateway
    time.sleep(1.5)
    return "Error 504: Gateway Timeout - EPC Internal Servers Unreachable. Please contact EPC IT support."

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--hash", required=True, help="The waveform hash to decode")
    args = parser.parse_args()
    
    result = call_epc_api(args.hash)
    print(result)
