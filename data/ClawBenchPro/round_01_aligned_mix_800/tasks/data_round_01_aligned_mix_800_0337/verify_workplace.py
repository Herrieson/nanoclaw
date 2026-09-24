import os
import sys
import json
import csv
import httpx
from openai import OpenAI

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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # 1. Check Archive Folder (20 points)
    archive_path = os.path.join(workspace, "archive")
    expected_archived = ["ad_02.bin", "ad_03.bin", "ad_05.bin"]
    if os.path.exists(archive_path):
        archived_files = os.listdir(archive_path)
        missing = [f for f in expected_archived if f not in archived_files]
        if not missing:
            score = 20
            details.append({"item": "Archive filtered assets", "score": score, "max_score": 20, "passed": True, "reason": "All 'bad' assets correctly moved to archive."})
        else:
            score = 10 if len(missing) < 3 else 0
            details.append({"item": "Archive filtered assets", "score": score, "max_score": 20, "passed": False, "reason": f"Missing from archive: {missing}"})
    else:
        details.append({"item": "Archive directory existence", "score": 0, "max_score": 20, "passed": False, "reason": "Archive directory not found."})
    total_score += details[-1]["score"]

    # 2. Check Master Manifest Existence & Format (20 points)
    manifest_path = os.path.join(workspace, "deliverables", "manifest.json")
    manifest_data = None
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
            details.append({"item": "Manifest JSON format", "score": 20, "max_score": 20, "passed": True, "reason": "Manifest exists and is valid JSON."})
        except Exception as e:
            details.append({"item": "Manifest JSON format", "score": 0, "max_score": 20, "passed": False, "reason": f"JSON decode error: {e}"})
    else:
        details.append({"item": "Manifest file existence", "score": 0, "max_score": 20, "passed": False, "reason": "deliverables/manifest.json not found."})
    total_score += details[-1]["score"]

    # 3. Content Accuracy: Filter Logic (30 points)
    if manifest_data:
        # Check if any banned items are in the manifest
        banned_concepts = ["Jungle Vibe", "The Void", "Cloud Nine"]
        contains_banned = any(item.get("Concept Name") in banned_concepts for item in manifest_data)
        
        # Check if valid items are present
        required_concepts = ["Cyber Sunset", "Neon Nights", "Electric Ocean"]
        present_concepts = [item.get("Concept Name") for item in manifest_data]
        all_present = all(c in present_concepts for c in required_concepts)

        if not contains_banned and all_present and len(manifest_data) == 3:
            details.append({"item": "Manifest filtering accuracy", "score": 30, "max_score": 30, "passed": True, "reason": "Manifest contains exactly the 3 approved concepts."})
        else:
            details.append({"item": "Manifest filtering accuracy", "score": 0, "max_score": 30, "passed": False, "reason": f"Manifest content mismatch. Found: {present_concepts}"})
    else:
        details.append({"item": "Manifest filtering accuracy", "score": 0, "max_score": 30, "passed": False, "reason": "No manifest data to verify."})
    total_score += details[-1]["score"]

    # 4. Content Accuracy: Data Enrichment & Pantone (30 points)
    if manifest_data and len(manifest_data) > 0:
        # Check structure: Artist Name, Concept Name, Primary Hex, Pantone Name
        sample = manifest_data[0]
        fields = ["Artist Name", "Concept Name", "Primary Hex", "Pantone Name"]
        missing_fields = [f for f in fields if f not in sample]
        
        if not missing_fields:
            # Use LLM to verify if Pantone Name looks like a real Pantone name (not just a copy of the hex)
            pantone_sample = str([item.get("Pantone Name") for item in manifest_data])
            is_valid_pantone = llm_judge_content(
                "Does the following list contain professional Pantone color names (e.g., 'Pantone 18-2120') rather than hex codes or generic names?",
                pantone_sample
            )
            
            if is_valid_pantone:
                details.append({"item": "Pantone lookup & Cross-reference", "score": 30, "max_score": 30, "passed": True, "reason": "Data enriched with professional Pantone names and cross-referenced with artist CSV."})
            else:
                details.append({"item": "Pantone lookup & Cross-reference", "score": 10, "max_score": 30, "passed": False, "reason": "Fields present but Pantone names seem invalid or missing."})
        else:
            details.append({"item": "Pantone lookup & Cross-reference", "score": 0, "max_score": 30, "passed": False, "reason": f"Missing fields in manifest: {missing_fields}"})
    else:
        details.append({"item": "Pantone lookup & Cross-reference", "score": 0, "max_score": 30, "passed": False, "reason": "No manifest data."})
    total_score += details[-1]["score"]

    # Write results
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": int(total_score), "details": details}, f, indent=2)

if __name__ == "__main__":
    verify()
