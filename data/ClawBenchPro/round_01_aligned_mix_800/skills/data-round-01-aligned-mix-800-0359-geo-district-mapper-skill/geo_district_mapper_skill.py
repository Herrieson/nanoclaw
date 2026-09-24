import json
import sys

def run(params_json):
    try:
        params = json.loads(params_json)
        codes = params.get("codes", [])
        mapping = {}
        for code in codes:
            if "-E" in code: mapping[code] = "East"
            elif "-S" in code: mapping[code] = "South"
            elif "-W" in code: mapping[code] = "West"
            elif "-N" in code: mapping[code] = "North"
            else: mapping[code] = "Unknown"
        return json.dumps(mapping)
    except:
        return "Error: Invalid Input"

if __name__ == "__main__":
    print(run(sys.argv[1] if len(sys.argv) > 1 else "{}"))
