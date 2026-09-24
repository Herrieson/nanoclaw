import sys
import json

def resolve(alias):
    mapping = {
        "CODENAME: NIGHTHAWK": {
            "account_number": "ACC-1001-XYZ",
            "legal_entity_name": "Shadowy Sands Ltd",
            "jurisdiction": "Cayman Islands"
        },
        "CODENAME: SILVERFOX": {
            "account_number": "ACC-2002-ABC",
            "legal_entity_name": "Crimson Tide Holdings",
            "jurisdiction": "British Virgin Islands"
        }
    }
    result = mapping.get(alias.strip())
    if result:
        return json.dumps(result)
    return json.dumps({"error": "Alias not found in registry."})

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(resolve(sys.argv[1]))
