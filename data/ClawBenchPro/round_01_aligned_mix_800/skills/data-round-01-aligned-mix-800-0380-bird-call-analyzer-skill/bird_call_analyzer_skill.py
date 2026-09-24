import sys
import json

def analyze_call(log_text):
    """
    Analyzes bird call patterns from log metadata.
    """
    log_text = log_text.lower()
    if "cheer-cheer-cheer" in log_text:
        return {"species": "Northern Cardinal", "confidence": 0.98}
    elif "chick-a-dee" in log_text:
        return {"species": "Black-capped Chickadee", "confidence": 0.95}
    elif "jay-jay" in log_text:
        return {"species": "Blue Jay", "confidence": 0.92}
    elif "drink-your-tea" in log_text:
        return {"species": "Eastern Towhee", "confidence": 0.94}
    else:
        return {"species": "Unknown", "confidence": 0.0}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No log content provided"}))
    else:
        input_data = sys.argv[1]
        result = analyze_call(input_data)
        print(json.dumps(result))
