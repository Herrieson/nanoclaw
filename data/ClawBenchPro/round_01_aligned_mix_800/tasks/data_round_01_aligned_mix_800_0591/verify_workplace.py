import os
import sys
import json
import csv
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

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

def calculate_ground_truth(workspace):
    total_cost = 0.0
    financials_dir = os.path.join(workspace, "financials")
    if os.path.exists(financials_dir):
        for root, _, files in os.walk(financials_dir):
            for f in files:
                filepath = os.path.join(root, f)
                if f.endswith(".json"):
                    try:
                        with open(filepath, "r", encoding="utf-8") as jf:
                            data = json.load(jf)
                            if data.get("status") == "VERIFIED":
                                for item in data.get("items", []):
                                    name = item.get("name", "")
                                    if name.startswith("Food") or name.startswith("Beverage"):
                                        total_cost += float(item.get("cost", 0.0))
                    except Exception:
                        pass
                elif f.endswith(".txt"):
                    try:
                        with open(filepath, "r", encoding="utf-8") as tf:
                            lines = tf.readlines()
                            if lines and lines[0].strip() == "STATUS: VERIFIED":
                                for line in lines:
                                    if line.strip().startswith("- Item: "):
                                        parts = line.split(" | Amount: $")
                                        if len(parts) == 2:
                                            item_name = parts[0].replace("- Item: ", "").strip()
                                            cost_str = parts[1].strip()
                                            if item_name.startswith("Food") or item_name.startswith("Beverage"):
                                                total_cost += float(cost_str)
                    except Exception:
                        pass
                        
    problem_vips = []
    reg_dir = os.path.join(workspace, "registrations")
    if os.path.exists(reg_dir):
        for root, _, files in os.walk(reg_dir):
            for f in files:
                if f.endswith(".csv"):
                    try:
                        with open(os.path.join(root, f), "r", encoding="utf-8") as cf:
                            reader = csv.DictReader(cf)
                            for row in reader:
                                if row.get("ticket_type") == "VIP":
                                    diet = row.get("diet_notes", "").strip().lower()
                                    if diet in ["", "none", "n/a"]:
                                        problem_vips.append(row.get("full_name", "").strip())
                    except Exception:
                        pass
    return total_cost, set(problem_vips)

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    score = 0
    details = []
    
    # Calculate truth deterministically
    gt_cost, gt_vips = calculate_ground_truth(workspace)
    
    audit_file = os.path.join(workspace, "desk", "audit.json")
    
    # 1. Check directory and file existence (20 points)
    if os.path.exists(audit_file):
        score += 20
        details.append({"item": "Result File Presence", "score": 20, "max_score": 20, "passed": True, "reason": "desk/audit.json found."})
    else:
        details.append({"item": "Result File Presence", "score": 0, "max_score": 20, "passed": False, "reason": "desk/audit.json is missing."})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": score, "details": details}, f, indent=2)
        return
        
    # 2. Check JSON validity (10 points)
    try:
        with open(audit_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        score += 10
        details.append({"item": "Valid JSON Format", "score": 10, "max_score": 10, "passed": True, "reason": "Successfully parsed JSON data."})
    except Exception as e:
        details.append({"item": "Valid JSON Format", "score": 0, "max_score": 10, "passed": False, "reason": f"Failed to parse JSON: {e}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": score, "details": details}, f, indent=2)
        return
        
    # 3. Flexible Key Extraction & Logic Evaluation (70 points)
    found_cost = None
    found_vips = None
    
    for k, v in data.items():
        if isinstance(v, (int, float)):
            found_cost = float(v)
        elif isinstance(v, list):
            found_vips = set([str(name).strip() for name in v])
            
    # Check Cost (35 points)
    if found_cost is not None:
        if abs(found_cost - gt_cost) < 0.01:
            score += 35
            details.append({"item": "Financial Audit Accuracy", "score": 35, "max_score": 35, "passed": True, "reason": f"Exact match for total cost: {found_cost}"})
        else:
            details.append({"item": "Financial Audit Accuracy", "score": 0, "max_score": 35, "passed": False, "reason": f"Cost mismatch. Expected around {gt_cost}, but found {found_cost}"})
    else:
        details.append({"item": "Financial Audit Accuracy", "score": 0, "max_score": 35, "passed": False, "reason": "No numeric value found for cost in JSON."})
        
    # Check VIPs (35 points)
    if found_vips is not None:
        missing = gt_vips - found_vips
        extra = found_vips - gt_vips
        if not missing and not extra:
            score += 35
            details.append({"item": "Attendee Audit Accuracy", "score": 35, "max_score": 35, "passed": True, "reason": "VIP list exact match."})
        else:
            penalty = len(missing) * 5 + len(extra) * 5
            vip_score = max(0, 35 - penalty)
            score += vip_score
            details.append({"item": "Attendee Audit Accuracy", "score": vip_score, "max_score": 35, "passed": vip_score == 35, "reason": f"VIPs mismatch. Missing {len(missing)}, Extra {len(extra)}."})
    else:
         details.append({"item": "Attendee Audit Accuracy", "score": 0, "max_score": 35, "passed": False, "reason": "No list value found for VIPs in JSON."})
         
    # Generate final output
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": score, "details": details}, f, indent=2)

if __name__ == "__main__":
    verify()
