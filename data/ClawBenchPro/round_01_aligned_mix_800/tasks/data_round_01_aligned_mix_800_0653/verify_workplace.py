import os
import sys
import json
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

def extract_all_values(obj):
    """Recursively extract all primitive values and lists from a JSON object."""
    values = []
    if isinstance(obj, dict):
        for v in obj.values():
            values.extend(extract_all_values(v))
    elif isinstance(obj, list):
        values.append(obj)
        for item in obj:
            values.extend(extract_all_values(item))
    else:
        values.append(obj)
    return values

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_dir = os.path.join(workspace, "deliverables")
    
    score_details = []
    total_score = 0
    
    # 1. Check directory existence
    if os.path.exists(deliverables_dir) and os.path.isdir(deliverables_dir):
        score_details.append({"item": "deliverables directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Directory found."})
        total_score += 10
    else:
        score_details.append({"item": "deliverables directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "Directory not found."})
        
    # 2. Check for JSON file
    json_files = []
    if os.path.exists(deliverables_dir):
        json_files = [f for f in os.listdir(deliverables_dir) if f.endswith(".json")]
    
    parsed_json = None
    if json_files:
        score_details.append({"item": "JSON file generated", "score": 10, "max_score": 10, "passed": True, "reason": f"Found {json_files[0]}."})
        total_score += 10
        
        # 3. Check JSON validity
        try:
            with open(os.path.join(deliverables_dir, json_files[0]), "r", encoding="utf-8") as f:
                parsed_json = json.load(f)
            score_details.append({"item": "JSON is valid", "score": 10, "max_score": 10, "passed": True, "reason": "Successfully parsed JSON."})
            total_score += 10
        except Exception as e:
            score_details.append({"item": "JSON is valid", "score": 0, "max_score": 10, "passed": False, "reason": f"Parse error: {e}"})
    else:
        score_details.append({"item": "JSON file generated", "score": 0, "max_score": 10, "passed": False, "reason": "No .json file found in deliverables."})
        score_details.append({"item": "JSON is valid", "score": 0, "max_score": 10, "passed": False, "reason": "No file to parse."})

    # Data to verify
    # Total valid hours: 17
    # Flagged students: Leo, Jake, Chloe
    
    hours_score = 0
    leo_score = 0
    jake_score = 0
    chloe_score = 0
    no_extra_flagged = True
    
    if parsed_json is not None:
        all_values = extract_all_values(parsed_json)
        
        # 4. Check total approved hours == 17
        has_17 = any(v == 17 or v == "17" for v in all_values)
        if has_17:
            hours_score = 40
            score_details.append({"item": "Calculated correct total approved hours (17)", "score": 40, "max_score": 40, "passed": True, "reason": "Found value 17 in JSON."})
        else:
            score_details.append({"item": "Calculated correct total approved hours (17)", "score": 0, "max_score": 40, "passed": False, "reason": "Value 17 not found in JSON."})
            
        # 5. Check flagged students
        # We look for strings in the JSON values or lists that contain these names
        flat_strings = [str(v).lower() for v in all_values if isinstance(v, str)]
        
        has_leo = any("leo" in s for s in flat_strings)
        has_jake = any("jake" in s for s in flat_strings)
        has_chloe = any("chloe" in s for s in flat_strings)
        
        if has_leo:
            leo_score = 10
            score_details.append({"item": "Flagged student list includes Leo", "score": 10, "max_score": 10, "passed": True, "reason": "Leo is correctly flagged."})
        else:
            score_details.append({"item": "Flagged student list includes Leo", "score": 0, "max_score": 10, "passed": False, "reason": "Leo is missing from the problem students."})
            
        if has_jake:
            jake_score = 10
            score_details.append({"item": "Flagged student list includes Jake", "score": 10, "max_score": 10, "passed": True, "reason": "Jake is correctly flagged."})
        else:
            score_details.append({"item": "Flagged student list includes Jake", "score": 0, "max_score": 10, "passed": False, "reason": "Jake is missing from the problem students."})
            
        if has_chloe:
            chloe_score = 10
            score_details.append({"item": "Flagged student list includes Chloe", "score": 10, "max_score": 10, "passed": True, "reason": "Chloe is correctly flagged."})
        else:
            score_details.append({"item": "Flagged student list includes Chloe", "score": 0, "max_score": 10, "passed": False, "reason": "Chloe is missing from the problem students."})
            
        # Verify no valid student was wrongly flagged
        # Valid students: Aarav, Maya, Sam, Zoe
        valid_students_found = []
        for v_student in ["aarav", "maya", "sam", "zoe"]:
            # If the JSON clearly uses lists for flagged students, we should ideally check just the lists
            # For robustness, we'll check if valid students are mentioned in a way that suggests they are flagged
            # However, since they shouldn't be in the flagged list, we use LLM for semantic verification of the JSON to ensure they aren't marked as problem students.
            pass
            
        if (hours_score + leo_score + jake_score + chloe_score) > 0:
            # Use LLM to verify that valid students are NOT in the problem list
            json_str = json.dumps(parsed_json)
            prompt = "Does this JSON include any of the following names: 'Aarav', 'Maya', 'Sam', 'Zoe' in the context of being 'flagged', 'problem', 'unapproved', or 'invalid' students? Answer 'YES' if they are wrongly flagged as problem students, otherwise answer 'NO'."
            is_wrongly_flagged = llm_judge_content(prompt, json_str)
            if is_wrongly_flagged:
                score_details.append({"item": "Penalty: Valid students wrongly flagged", "score": -10, "max_score": 0, "passed": False, "reason": "LLM detected that a valid student was included in the problem list."})
                total_score -= 10
    else:
        score_details.append({"item": "Calculated correct total approved hours (17)", "score": 0, "max_score": 40, "passed": False, "reason": "No JSON to verify."})
        score_details.append({"item": "Flagged student list includes Leo", "score": 0, "max_score": 10, "passed": False, "reason": "No JSON to verify."})
        score_details.append({"item": "Flagged student list includes Jake", "score": 0, "max_score": 10, "passed": False, "reason": "No JSON to verify."})
        score_details.append({"item": "Flagged student list includes Chloe", "score": 0, "max_score": 10, "passed": False, "reason": "No JSON to verify."})

    total_score += hours_score + leo_score + jake_score + chloe_score
    total_score = max(0, min(100, total_score))
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)

if __name__ == "__main__":
    main()
