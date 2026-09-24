import os
import sys
import json
import csv
import httpx
from openai import OpenAI
import glob

# Configuration for LLM
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

def get_ground_truth(workspace):
    # Calculate Ground Truth based on env_builder logic
    unapproved_servers = []
    trad_ingredients = set()

    # 1. Process Volunteers
    vol_file = os.path.join(workspace, "system_export/volunteer_dump.csv")
    if os.path.exists(vol_file):
        with open(vol_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                v_id = row["Volunteer_ID"]
                role = row["Assigned_Role"]
                name = row["Full_Name"]
                
                if role == "Serving" and not v_id.startswith("SYS_TEST"):
                    cert_path = os.path.join(workspace, f"compliance_certs/{v_id}_record.json")
                    is_approved = False
                    if os.path.exists(cert_path):
                        with open(cert_path, "r") as cf:
                            cert = json.load(cf)
                            if cert.get("status") == "Passed":
                                is_approved = True
                    
                    if not is_approved:
                        unapproved_servers.append(name)

    # 2. Process Recipes
    recipe_files = glob.glob(os.path.join(workspace, "global_recipes/**/*"), recursive=True)
    for rf_path in recipe_files:
        if os.path.isfile(rf_path):
            try:
                with open(rf_path, "r") as f:
                    data = json.load(f)
                    if data.get("metadata", {}).get("category") == "Traditional Filipino":
                        trad_ingredients.update(data.get("ingredients", []))
            except:
                continue
    
    return sorted(unapproved_servers), sorted(list(trad_ingredients))

def run_evaluation():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    # 1. Check Directory and File Existence (10 points)
    deliverables_dir = os.path.join(workspace, "deliverables")
    if os.path.exists(deliverables_dir) and os.path.isdir(deliverables_dir):
        files = [f for f in os.listdir(deliverables_dir) if os.path.isfile(os.path.join(deliverables_dir, f))]
        if files:
            score_details.append({"item": "Deliverables folder and file exist", "score": 10, "max_score": 10, "passed": True, "reason": f"Found file: {files[0]}"})
            target_file = os.path.join(deliverables_dir, files[0])
            with open(target_file, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            score_details.append({"item": "Deliverables folder exists but is empty", "score": 5, "max_score": 10, "passed": False, "reason": "No summary file found"})
            content = ""
    else:
        score_details.append({"item": "Deliverables folder not found", "score": 0, "max_score": 10, "passed": False, "reason": "Directory 'deliverables' missing"})
        content = ""

    # Get Truth
    gt_servers, gt_ingredients = get_ground_truth(workspace)

    if content:
        # 2. Check Unapproved Servers (40 points)
        # We use LLM to check if the names are correctly listed because formatting might vary
        server_check_prompt = f"Does the following content list these specific volunteer names as unapproved or missing safety certificates? Expected names: {', '.join(gt_servers[:20])}... (total {len(gt_servers)} names). Note: Ensure it DOES NOT include system test IDs."
        if llm_judge_content(server_check_prompt, content):
            score_details.append({"item": "Correct Unapproved Servers List", "score": 40, "max_score": 40, "passed": True, "reason": "LLM verified the unapproved server list matches requirements."})
        else:
            # Partial credit check via simple presence
            present_count = sum(1 for name in gt_servers if name in content)
            partial = int((present_count / len(gt_servers)) * 20) if gt_servers else 0
            score_details.append({"item": "Correct Unapproved Servers List (Partial/Failed)", "score": partial, "max_score": 40, "passed": False, "reason": f"LLM rejected or names missing. Found {present_count}/{len(gt_servers)} matches."})

        # 3. Check Ingredients (40 points)
        # Strict check: Traditional Filipino only. No Fusion or Modern.
        # Fusion ingredients like "Taco shells" or "Truffle oil" should NOT be here.
        ingredient_check_prompt = f"Does the content provide a combined ingredient list for 'Traditional Filipino' recipes? It should include items like {', '.join(gt_ingredients)}. It must NOT include 'Truffle oil' or 'Taco shells'. Is it accurate?"
        if llm_judge_content(ingredient_check_prompt, content):
            score_details.append({"item": "Correct Ingredients Aggregation", "score": 40, "max_score": 40, "passed": True, "reason": "LLM verified the traditional Filipino ingredient list."})
        else:
            score_details.append({"item": "Correct Ingredients Aggregation", "score": 0, "max_score": 40, "passed": False, "reason": "LLM rejected the ingredient list (possibly included Modern/Fusion or missed items)."})

        # 4. Filter Check: SYS_TEST (10 points)
        if "SYS_TEST" not in content:
            score_details.append({"item": "Filtering System Artifacts", "score": 10, "max_score": 10, "passed": True, "reason": "No SYS_TEST strings found in final output."})
        else:
            score_details.append({"item": "Filtering System Artifacts", "score": 0, "max_score": 10, "passed": False, "reason": "Output contains SYS_TEST IDs which should have been ignored."})

    total_score = sum(d["score"] for d in score_details)
    
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)

if __name__ == "__main__":
    run_evaluation()
