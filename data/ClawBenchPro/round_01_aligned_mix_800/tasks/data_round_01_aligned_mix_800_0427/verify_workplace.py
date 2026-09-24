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
    # 1. Active tenants
    active_tenants = set()
    tenants_dir = os.path.join(workspace, "property_data", "tenants")
    if os.path.exists(tenants_dir):
        for root, dirs, files in os.walk(tenants_dir):
            for file in files:
                if file == "roster.json":
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        try:
                            data = json.load(f)
                            for item in data:
                                if item.get("status") == "active":
                                    active_tenants.add(item.get("name"))
                        except Exception:
                            pass
    
    # 2. Trespassers
    trespassers = set()
    logs_dir = os.path.join(workspace, "lobby_logs")
    if os.path.exists(logs_dir):
        for root, dirs, files in os.walk(logs_dir):
            for file in files:
                if file.endswith(".log"):
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        for line in f:
                            if "EVENT: ENTRY" in line:
                                parts = line.split("|")
                                person = ""
                                for p in parts:
                                    if "PERSON:" in p:
                                        person = p.split("PERSON:")[1].strip()
                                if person and person not in active_tenants:
                                    trespassers.add(person)
    unauthorized_tenants = sorted(list(trespassers))

    # 3. Policy & Vendors
    approved_vendors = set()
    policy_file = os.path.join(workspace, "property_data", "contracts", "policy.yaml")
    if os.path.exists(policy_file):
        with open(policy_file, 'r', encoding='utf-8') as f:
            for line in f:
                if "current_approved_list:" in line:
                    csv_name = line.split(":")[1].strip()
                    csv_path = os.path.join(workspace, "property_data", "vendors", csv_name)
                    if os.path.exists(csv_path):
                        with open(csv_path, 'r', encoding='utf-8') as cf:
                            reader = csv.DictReader(cf)
                            for row in reader:
                                approved_vendors.add(row["VendorName"])
    
    # 4. Invoices
    unauthorized_vendors = set()
    unauthorized_cost = 0.0
    invoices_dir = os.path.join(workspace, "financials", "invoices")
    if os.path.exists(invoices_dir):
        for root, dirs, files in os.walk(invoices_dir):
            for file in files:
                if file.endswith(".json") and file.startswith("inv_"):
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        try:
                            inv = json.load(f)
                            vendor = inv.get("vendor")
                            status = inv.get("status")
                            amt = inv.get("amount", 0.0)
                            if vendor not in approved_vendors:
                                if status in ["PAID", "PENDING"]:
                                    unauthorized_vendors.add(vendor)
                                    unauthorized_cost += amt
                        except Exception:
                            pass
    unauthorized_vendors = sorted(list(unauthorized_vendors))

    return {
        "unauthorized_tenants": unauthorized_tenants,
        "unauthorized_vendors": unauthorized_vendors,
        "unauthorized_cost": unauthorized_cost
    }

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    truth = calculate_ground_truth(workspace)
    
    report_dir = os.path.join(workspace, "audit_deliverables")
    report_file = os.path.join(report_dir, "discrepancy_report.json")
    
    # 1. Check directory and file existence
    if os.path.exists(report_file):
        score_details.append({"item": "Deliverable File Exists", "score": 10, "max_score": 10, "passed": True, "reason": "discrepancy_report.json found."})
        total_score += 10
    else:
        score_details.append({"item": "Deliverable File Exists", "score": 0, "max_score": 10, "passed": False, "reason": "discrepancy_report.json missing."})
        
        # Fast fail if file not exists
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 2. Check JSON validity and Keys
    try:
        with open(report_file, 'r', encoding='utf-8') as f:
            agent_data = json.load(f)
            
        required_keys = {"unauthorized_vendors", "unauthorized_cost", "unauthorized_tenants"}
        if required_keys.issubset(set(agent_data.keys())):
            score_details.append({"item": "JSON Schema & Keys", "score": 10, "max_score": 10, "passed": True, "reason": "All required keys are present in JSON."})
            total_score += 10
        else:
            missing = required_keys - set(agent_data.keys())
            score_details.append({"item": "JSON Schema & Keys", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing keys: {missing}"})
            
    except Exception as e:
        score_details.append({"item": "JSON Schema & Keys", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON format: {e}"})
        # Fast fail if invalid JSON
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 3. Verify unauthorized_vendors
    agent_vendors = agent_data.get("unauthorized_vendors", [])
    if isinstance(agent_vendors, list) and agent_vendors == truth["unauthorized_vendors"]:
        score_details.append({"item": "Unauthorized Vendors Match", "score": 20, "max_score": 20, "passed": True, "reason": "Accurately identified all unauthorized vendors from non-VOID invoices."})
        total_score += 20
    else:
        score_details.append({"item": "Unauthorized Vendors Match", "score": 0, "max_score": 20, "passed": False, "reason": "Mismatch in unauthorized vendors list."})

    # 4. Verify unauthorized_tenants
    agent_tenants = agent_data.get("unauthorized_tenants", [])
    if isinstance(agent_tenants, list) and agent_tenants == truth["unauthorized_tenants"]:
        score_details.append({"item": "Trespasser Tenants Match", "score": 30, "max_score": 30, "passed": True, "reason": "Accurately identified all trespassing tenants from lobby logs."})
        total_score += 30
    else:
        score_details.append({"item": "Trespasser Tenants Match", "score": 0, "max_score": 30, "passed": False, "reason": "Mismatch in unauthorized tenants list (likely missed evicted tenants or wrong entry detection)."})

    # 5. Verify unauthorized_cost
    agent_cost = agent_data.get("unauthorized_cost", 0)
    try:
        agent_cost = float(agent_cost)
        if abs(agent_cost - truth["unauthorized_cost"]) < 0.01:
            score_details.append({"item": "Unauthorized Cost Precision Match", "score": 30, "max_score": 30, "passed": True, "reason": "Perfect match for total unauthorized cost."})
            total_score += 30
        else:
            score_details.append({"item": "Unauthorized Cost Precision Match", "score": 0, "max_score": 30, "passed": False, "reason": f"Mismatch in cost calculation. Expected {truth['unauthorized_cost']}, got {agent_cost}."})
    except Exception:
        score_details.append({"item": "Unauthorized Cost Precision Match", "score": 0, "max_score": 30, "passed": False, "reason": "Cost is not a valid numeric value."})

    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
