import json
import sys

def main():
    # Simple Mock: 5-10 -> Potawatomi Crafts, 11-17 -> Navajo Code Talkers
    mapping = {
        "brackets": [
            {"min": 5, "max": 10, "exhibit": "Illinois Potawatomi Crafts"},
            {"min": 11, "max": 17, "exhibit": "Navajo Code Talkers Comms Tent"}
        ],
        "status": "Official 2024 Guidelines"
    }
    print(json.dumps(mapping))

if __name__ == "__main__":
    main()
