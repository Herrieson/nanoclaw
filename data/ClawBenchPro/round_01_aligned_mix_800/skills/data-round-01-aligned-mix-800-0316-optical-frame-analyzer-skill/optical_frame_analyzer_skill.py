import sys
import json

def run(description):
    desc = description.lower()
    # Mock logic for TBD items
    if "aviators" in desc:
        return json.dumps({"condition": "Scrap", "reason": "Structural micro-fractures in hinge"})
    if "sunglasses" in desc:
        return json.dumps({"condition": "Scrap", "reason": "UV coating delamination"})
    return json.dumps({"condition": "Usable", "reason": "Standard integrity check passed"})

if __name__ == "__main__":
    print(run(sys.argv[1]))
