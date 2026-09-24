import os
import sys
import json
import re
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Initialize client, strictly disabling SSL verification
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict data validation assistant. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[File Content]:\n{file_content}"}
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def extract_data(obj, numbers, strings):
    """Recursively extract all numeric values and strings from a JSON object."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            strings.append(str(k))
            extract_data(v, numbers, strings)
    elif isinstance(obj, list):
        for item in obj:
            extract_data(item, numbers, strings)
    elif isinstance(obj, (int, float)):
        numbers.append(float(obj))
    elif isinstance(obj, str):
        strings.append(obj)
        # Also attempt to parse hidden numbers inside strings (e.g., "$1500.74")
        nums = re.findall(r'-?\d+(?:\.\d+)?', obj)
        for n in nums:
            try:
                numbers.append(float(n))
            except ValueError:
                pass

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    desk_dir = os.path.join(workspace, "desk")
    audit_file = os.path.join(desk_dir, "audit.json")
    
    details = []
    total_score = 0
    
    # 1. Check if the directory and file exist (10 pts)
    if os.path.exists(audit_file):
        details.append({"item": "Audit file exists in desk directory", "score": 10, "max_score": 10, "passed": True, "reason": "desk/audit.json found."})
        total_score += 10
    else:
        details.append({"item": "Audit file exists in desk directory", "score": 0, "max_score": 10, "passed": False, "reason": "desk/audit.json not found."})
        
    # Variables for JSON extraction
    is_valid_json = False
    data = None
    numbers = []
    strings = []
    
    # 2. Check JSON validity (10 pts)
    if os.path.exists(audit_file):
        try:
            with open(audit_file, "r", encoding="utf-8") as f:
                content = f.read()
                data = json.loads(content)
            is_valid_json = True
            details.append({"item": "JSON format validity", "score": 10, "max_score": 10, "passed": True, "reason": "File is a valid JSON."})
            total_score += 10
            
            # Extract data
            extract_data(data, numbers, strings)
        except Exception as e:
            details.append({"item": "JSON format validity", "score": 0, "max_score": 10, "passed": False, "reason": f"Failed to parse JSON: {e}"})
    else:
        details.append({"item": "JSON format validity", "score": 0, "max_score": 10, "passed": False, "reason": "File missing."})

    # 3. Check for accurate Total Food & Beverage Cost (35 pts)
    if is_valid_json:
        # Expected: 1050.50 + 320.25 + 89.99 + 40.00 = 1500.74
        found_cost = any(abs(n - 1500.74) < 0.01 for n in numbers)
        if found_cost:
            details.append({"item": "Total Food and Beverage cost calculation", "score": 35, "max_score": 35, "passed": True, "reason": "Correctly extracted 1500.74 from receipts."})
            total_score += 35
        else:
            details.append({"item": "Total Food and Beverage cost calculation", "score": 0, "max_score": 35, "passed": False, "reason": "Did not find the exact calculated value 1500.74."})
    else:
        details.append({"item": "Total Food and Beverage cost calculation", "score": 0, "max_score": 35, "passed": False, "reason": "File missing or invalid."})

    # 4. Check Problematic VIP List Completeness (20 pts)
    if is_valid_json:
        expected_vips = ["alice walker", "margaret atwood", "toni morrison"]
        vips_found = 0
        for expected_name in expected_vips:
            if any(expected_name in s.lower() for s in strings):
                vips_found += 1
        
        vip_score = int((vips_found / 3) * 20)
        details.append({"item": "Problematic VIP list completeness", "score": vip_score, "max_score": 20, "passed": (vip_score == 20), "reason": f"Found {vips_found}/3 problematic VIPs."})
        total_score += vip_score
    else:
        details.append({"item": "Problematic VIP list completeness", "score": 0, "max_score": 20, "passed": False, "reason": "File missing or invalid."})

    # 5. Hallucination / False Positives Check for VIPs (15 pts)
    if is_valid_json:
        false_positives = ["bob general", "han kang", "stephen king", "jane doe", "james baldwin"]
        fp_found = 0
        for fp in false_positives:
            if any(fp in s.lower() for s in strings):
                fp_found += 1
        
        fp_score = 15 - (fp_found * 5)
        fp_score = max(0, fp_score)
        details.append({"item": "VIP list false positives penalty", "score": fp_score, "max_score": 15, "passed": (fp_score == 15), "reason": f"Detected {fp_found} false positive attendees."})
        total_score += fp_score
    else:
        details.append({"item": "VIP list false positives penalty", "score": 0, "max_score": 15, "passed": False, "reason": "File missing or invalid."})

    # 6. LLM Semantic Verification for Clean Output (10 pts)
    if is_valid_json:
        all_text = " ".join(strings)
        prompt = (
            "Analyze the following extracted JSON strings. Does it look strictly like clean, professional data representation? "
            "It MUST NOT contain any conversational filler, apologies, or lengthy explanations (like 'Here is the data', 'Sorry for the delay', 'The total cost is'). "
            "Answer YES if it is perfectly clean and minimal data, answer NO if it contains conversational fluff."
        )
        is_clean = llm_judge_content(prompt, all_text)
        if is_clean:
            details.append({"item": "LLM output cleanliness check", "score": 10, "max_score": 10, "passed": True, "reason": "Output is professional and contains no conversational filler."})
            total_score += 10
        else:
            details.append({"item": "LLM output cleanliness check", "score": 0, "max_score": 10, "passed": False, "reason": "LLM detected conversational filler or non-professional formatting in the JSON payload."})
    else:
        details.append({"item": "LLM output cleanliness check", "score": 0, "max_score": 10, "passed": False, "reason": "File missing or invalid."})

    # Write final score result
    result = {
        "total_score": total_score,
        "details": details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
