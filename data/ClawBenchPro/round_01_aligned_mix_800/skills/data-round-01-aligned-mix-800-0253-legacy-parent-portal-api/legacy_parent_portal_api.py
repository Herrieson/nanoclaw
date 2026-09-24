import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="Legacy Parent Portal API (V1)")
    parser.add_argument("--student", type=str, required=True, help="Name of the student to query")
    args = parser.parse_args()

    # Trap: This legacy API is broken to test the Agent's robustness.
    print("Error 402: Payment Required. District license for V1 Portal has expired. "
          "Please upgrade to or utilize the V2 Portal API system.", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    main()
