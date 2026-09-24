import sys
import json

def lookup(asset_id):
    registry = {
        "ASSET-9902": {"name": "Case 580 Backhoe", "type": "backhoe", "heavy": True},
        "ASSET-7721": {"name": "Ford F-150 Pickup", "type": "truck", "heavy": True},
        "ASSET-1102": {"name": "Hand Drill", "type": "tool", "heavy": False}
    }
    return json.dumps(registry.get(asset_id, {"error": "Asset not found"}))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(lookup(sys.argv[1]))
    else:
        print("Error: Missing Asset ID")
