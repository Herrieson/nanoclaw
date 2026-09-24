import os
import sys
import json
import httpx
from openai import OpenAI

# Configuration for potential LLM usage (though this task is primarily structured data)
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    target_file = os.path.join(workspace, "investigation/suspects.json")
    
    # 1. Check if the output file exists (10 points)
    if os.path.exists(target_file):
        score += 10
        details.append({"item": "Check suspects.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found."})
    else:
        details.append({"item": "Check suspects.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File investigation/suspects.json missing."})
        # If file doesn't exist, we can't check the rest
        write_score(score, details)
        return

    # 2. Check JSON validity and structure (20 points)
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        
        if isinstance(data, dict):
            score += 20
            details.append({"item": "Valid JSON format", "score": 20, "max_score": 20, "passed": True, "reason": "JSON parsed successfully and is a dictionary."})
        else:
            details.append({"item": "Valid JSON format", "score": 0, "max_score": 20, "passed": False, "reason": "File is JSON but not a dictionary (key-value pair of names)."})
            write_score(score, details)
            return
    except Exception as e:
        details.append({"item": "Valid JSON format", "score": 0, "max_score": 20, "passed": False, "reason": f"JSON decode error: {e}"})
        write_score(score, details)
        return

    # 3. Content Accuracy (70 points)
    # Expected Ground Truth (Calculated from env_builder):
    # Marcus Vance (EMP_042): 45m
    # Tommy Cash (EMP_113): 15m + 30m = 45m
    # Victor Creed (EMP_007): 120m
    # Sarah Jenkins (EMP_099): 10m
    expected = {
        "Marcus Vance": 45,
        "Tommy Cash": 45,
        "Victor Creed": 120,
        "Sarah Jenkins": 10
    }
    
    # Check if extra people are included (Hallucination/Noise check)
    all_keys = set(data.keys())
    expected_keys = set(expected.keys())
    
    extra_keys = all_keys - expected_keys
    missing_keys = expected_keys - all_keys
    
    # Score calculation for content
    content_score = 0
    
    # 3a. Correct values for expected keys (40 points)
    correct_values = 0
    for name, minutes in expected.items():
        if name in data and data[name] == minutes:
            correct_values += 1
    
    val_score = (correct_values / len(expected)) * 50
    score += val_score
    details.append({
        "item": "Suspect identification and calculation",
        "score": int(val_score),
        "max_score": 50,
        "passed": correct_values == len(expected),
        "reason": f"Correctly identified {correct_values}/{len(expected)} suspects with precise minutes."
    })

    # 3b. Absence of false positives (20 points)
    if len(extra_keys) == 0:
        score += 20
        details.append({"item": "No false positives", "score": 20, "max_score": 20, "passed": True, "reason": "No incorrect people or noise (like 2022 data) included."})
    else:
        # Deduct 5 points per extra key, floor at 0
        deduction = len(extra_keys) * 10
        fp_score = max(0, 20 - deduction)
        score += fp_score
        details.append({"item": "No false positives", "score": int(fp_score), "max_score": 20, "passed": False, "reason": f"Found extra entries: {list(extra_keys)}"})

    write_score(int(score), details)

def write_score(score, details):
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": score, "details": details}, f, indent=2)

if __name__ == "__main__":
    verify()
