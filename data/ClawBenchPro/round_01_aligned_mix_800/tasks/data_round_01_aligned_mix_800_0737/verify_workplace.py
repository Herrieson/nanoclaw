import os
import sys
import json
import csv
import httpx
from openai import OpenAI

# ----------------------------------------------------------------
# Configuration & LLM Setup
# ----------------------------------------------------------------

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

# ----------------------------------------------------------------
# Validation Logic
# ----------------------------------------------------------------

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    score_details = []
    
    # 1. Check Directory Structure (15 points)
    archive_path = os.path.join(workspace, "archive")
    deliverables_path = os.path.join(workspace, "deliverables")
    
    archive_exists = os.path.isdir(archive_path)
    deliverables_exists = os.path.isdir(deliverables_path)
    
    score_details.append({
        "item": "Directory creation (archive & deliverables)",
        "score": 15 if archive_exists and deliverables_exists else (7 if archive_exists or deliverables_exists else 0),
        "max_score": 15,
        "passed": archive_exists and deliverables_exists,
        "reason": f"Archive: {archive_exists}, Deliverables: {deliverables_exists}"
    })

    # 2. Archive Filtering Logic (30 points)
    # Target files to move: ad_02 (Papyrus), ad_03 (#000000), ad_05 (Comic Sans / #FFFFFF)
    # Remaining files in campaign_assets should be: ad_01, ad_04, ad_06
    expected_archived = ["ad_02_jungle.json", "ad_03_void.json", "ad_05_cloud.json"]
    expected_surviving = ["ad_01_cyber.json", "ad_04_neon.json", "ad_06_ocean.json"]
    
    actual_archived = os.listdir(archive_path) if archive_exists else []
    actual_assets = os.listdir(os.path.join(workspace, "campaign_assets")) if os.path.isdir(os.path.join(workspace, "campaign_assets")) else []
    
    # Correctness of Move
    correct_move_count = sum(1 for f in expected_archived if f in actual_archived)
    incorrect_stay_count = sum(1 for f in expected_archived if f in actual_assets)
    
    archive_score = (correct_move_count / 3) * 30
    if incorrect_stay_count > 0: archive_score -= (incorrect_stay_count * 10)
    archive_score = max(0, int(archive_score))
    
    score_details.append({
        "item": "Correctly filtering and archiving mediocre concepts",
        "score": archive_score,
        "max_score": 30,
        "passed": archive_score == 30,
        "reason": f"Successfully archived {correct_move_count}/3 files. {incorrect_stay_count} bad files remained."
    })

    # 3. Deliverables JSON Manifest (45 points)
    manifest_path = None
    # Look for any JSON in deliverables
    if deliverables_exists:
        for f in os.listdir(deliverables_path):
            if f.endswith(".json"):
                manifest_path = os.path.join(deliverables_path, f)
                break
    
    manifest_score = 0
    if manifest_path:
        try:
            with open(manifest_path, 'r') as f:
                data = json.load(f)
            
            # Data should be a list or dict containing 3 approved artists: Leo Vance, Ava Smith, Liam Gallagher
            manifest_str = json.dumps(data)
            has_leo = "Leo Vance" in manifest_str and "Cyber Sunset" in manifest_str
            has_ava = "Ava Smith" in manifest_str and "Neon Nights" in manifest_str
            has_liam = "Liam Gallagher" in manifest_str and "Electric Ocean" in manifest_str
            
            # Check for bad artists (should NOT be there)
            has_bad = any(name in manifest_str for name in ["Mia Wallace", "Noah Trent", "Zoe Barnes"])
            
            if has_leo: manifest_score += 15
            if has_ava: manifest_score += 15
            if has_liam: manifest_score += 15
            if has_bad: manifest_score -= 20
            
            manifest_score = max(0, manifest_score)
        except:
            manifest_score = 0
            
    score_details.append({
        "item": "Unified JSON manifest in deliverables",
        "score": manifest_score,
        "max_score": 45,
        "passed": manifest_score >= 40,
        "reason": "Checking cross-referencing of CSV data with surviving concepts."
    })

    # 4. LLM Tone Check (10 points)
    # The prompt implies a specific professional but slightly aesthetic-focused vibe.
    # While no specific email was requested, the manifest structure or any notes should be clean.
    # We will check the JSON structure quality using LLM.
    llm_score = 0
    if manifest_path:
        with open(manifest_path, 'r') as f:
            content = f.read()
        prompt = "Does this JSON manifest clearly pair 'Artist Name', 'Concept Name', and 'Primary Color' in a clean, professional way suitable for an Art Director?"
        if llm_judge_content(prompt, content):
            llm_score = 10
            
    score_details.append({
        "item": "Manifest format quality (LLM Judge)",
        "score": llm_score,
        "max_score": 10,
        "passed": llm_score == 10,
        "reason": "Evaluation of the JSON output structure and readability."
    })

    # Final Calculation
    total_score = sum(d["score"] for d in score_details)
    
    output = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    main()
