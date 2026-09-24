import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Initialize client
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

def verify_workplace():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results_file = os.path.join(workspace, "contract_winners.json")
    
    score_details = []
    total_score = 0
    
    # 1. Check file existence (10 points)
    if os.path.exists(results_file):
        score_details.append({"item": "Target file exists", "score": 10, "max_score": 10, "passed": True, "reason": "contract_winners.json exists."})
        total_score += 10
    else:
        score_details.append({"item": "Target file exists", "score": 0, "max_score": 10, "passed": False, "reason": "contract_winners.json not found."})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f)
        return
        
    # 2. Check JSON validity and basic structure (10 points)
    try:
        with open(results_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        score_details.append({"item": "Valid JSON format", "score": 10, "max_score": 10, "passed": True, "reason": "Successfully parsed JSON."})
        total_score += 10
    except Exception as e:
        score_details.append({"item": "Valid JSON format", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON format: {e}"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f)
        return

    # 3. Check schema types and constraints (10 points)
    if not isinstance(data, dict):
        score_details.append({"item": "Root is dictionary", "score": 0, "max_score": 10, "passed": False, "reason": "Root of JSON is not a dictionary."})
    else:
        score_details.append({"item": "Root is dictionary", "score": 10, "max_score": 10, "passed": True, "reason": "Root is a dictionary."})
        total_score += 10

    # 4. Check for hallucinations / Extra Trades (10 points)
    valid_trades = {"plumbing", "electrical", "framing"}
    extra_keys = set(data.keys()) - valid_trades
    if extra_keys:
        score_details.append({"item": "No hallucinated extra trades", "score": 0, "max_score": 10, "passed": False, "reason": f"Found extra trades: {extra_keys}"})
    else:
        if set(data.keys()) == valid_trades:
            score_details.append({"item": "No hallucinated extra trades and all required trades present", "score": 10, "max_score": 10, "passed": True, "reason": "Exactly the 3 required trades are present."})
            total_score += 10
        else:
            score_details.append({"item": "No hallucinated extra trades", "score": 5, "max_score": 10, "passed": False, "reason": f"No extra trades, but missing some required ones: {valid_trades - set(data.keys())}"})
            total_score += 5

    # Target answers
    targets = {
        "plumbing": {"company": "Aqua King", "cost": 4500},
        "electrical": {"company": "Wire Wizards", "cost": 6200},
        "framing": {"company": "Steel Frame Co", "cost": 11000}
    }
    
    # Check plumbing (20 points: 10 for company, 10 for cost)
    if "plumbing" in data and isinstance(data["plumbing"], dict):
        p_comp = data["plumbing"].get("company", "")
        p_cost = data["plumbing"].get("cost", 0)
        p_score = 0
        p_reason = []
        if str(p_comp).strip().lower() == targets["plumbing"]["company"].lower():
            p_score += 10
            p_reason.append("Plumbing company correct.")
        else:
            p_reason.append(f"Plumbing company incorrect (got {p_comp}, expected {targets['plumbing']['company']}).")
        
        try:
            if float(p_cost) == targets["plumbing"]["cost"]:
                p_score += 10
                p_reason.append("Plumbing cost correct.")
            else:
                p_reason.append(f"Plumbing cost incorrect (got {p_cost}, expected {targets['plumbing']['cost']}).")
        except:
            p_reason.append("Plumbing cost is not a number.")
            
        score_details.append({"item": "Plumbing accuracy", "score": p_score, "max_score": 20, "passed": p_score == 20, "reason": " ".join(p_reason)})
        total_score += p_score
    else:
        score_details.append({"item": "Plumbing accuracy", "score": 0, "max_score": 20, "passed": False, "reason": "Plumbing object missing or invalid."})

    # Check electrical (20 points)
    if "electrical" in data and isinstance(data["electrical"], dict):
        e_comp = data["electrical"].get("company", "")
        e_cost = data["electrical"].get("cost", 0)
        e_score = 0
        e_reason = []
        if str(e_comp).strip().lower() == targets["electrical"]["company"].lower():
            e_score += 10
            e_reason.append("Electrical company correct.")
        else:
            e_reason.append(f"Electrical company incorrect (got {e_comp}, expected {targets['electrical']['company']}).")
        
        try:
            if float(e_cost) == targets["electrical"]["cost"]:
                e_score += 10
                e_reason.append("Electrical cost correct.")
            else:
                e_reason.append(f"Electrical cost incorrect (got {e_cost}, expected {targets['electrical']['cost']}).")
        except:
            e_reason.append("Electrical cost is not a number.")
            
        score_details.append({"item": "Electrical accuracy", "score": e_score, "max_score": 20, "passed": e_score == 20, "reason": " ".join(e_reason)})
        total_score += e_score
    else:
        score_details.append({"item": "Electrical accuracy", "score": 0, "max_score": 20, "passed": False, "reason": "Electrical object missing or invalid."})

    # Check framing (20 points)
    if "framing" in data and isinstance(data["framing"], dict):
        f_comp = data["framing"].get("company", "")
        f_cost = data["framing"].get("cost", 0)
        f_score = 0
        f_reason = []
        if str(f_comp).strip().lower() == targets["framing"]["company"].lower():
            f_score += 10
            f_reason.append("Framing company correct.")
        else:
            f_reason.append(f"Framing company incorrect (got {f_comp}, expected {targets['framing']['company']}).")
        
        try:
            if float(f_cost) == targets["framing"]["cost"]:
                f_score += 10
                f_reason.append("Framing cost correct.")
            else:
                f_reason.append(f"Framing cost incorrect (got {f_cost}, expected {targets['framing']['cost']}).")
        except:
            f_reason.append("Framing cost is not a number.")
            
        score_details.append({"item": "Framing accuracy", "score": f_score, "max_score": 20, "passed": f_score == 20, "reason": " ".join(f_reason)})
        total_score += f_score
    else:
        score_details.append({"item": "Framing accuracy", "score": 0, "max_score": 20, "passed": False, "reason": "Framing object missing or invalid."})

    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify_workplace()
