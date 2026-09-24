import os
import sys
import json
import httpx
from openai import OpenAI

# Configuration for potential LLM usage (though this task is primarily structured)
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
    results = []
    total_score = 0
    
    target_dir = os.path.join(workspace, "party_prep")
    target_file = os.path.join(target_dir, "party_info.json") # Looking for a JSON in the new folder
    
    # 1. Check Directory and File Existence (10 points)
    dir_exists = os.path.exists(target_dir)
    file_exists = False
    if dir_exists:
        # Check for any json file if they named it differently
        json_files = [f for f in os.listdir(target_dir) if f.endswith('.json')]
        if json_files:
            target_file = os.path.join(target_dir, json_files[0])
            file_exists = True

    score_1 = 10 if (dir_exists and file_exists) else 0
    total_score += score_1
    results.append({"item": "Directory and JSON file creation", "score": score_1, "max_score": 10, "passed": score_1 == 10, "reason": "party_prep folder and JSON file exist" if score_1 == 10 else "Missing folder or JSON file"})

    # 2. Schema and Parsing (10 points)
    data = None
    parse_success = False
    if file_exists:
        try:
            with open(target_file, 'r') as f:
                data = json.load(f)
            parse_success = True
        except Exception:
            parse_success = False
            
    score_2 = 10 if parse_success else 0
    total_score += score_2
    results.append({"item": "JSON Schema Validity", "score": score_2, "max_score": 10, "passed": parse_success, "reason": "Valid JSON format" if parse_success else "Invalid JSON"})

    if data:
        # Convert list to dict for easier checking if it's a list
        if isinstance(data, list):
            data_map = {item.get('name') or item.get('client_name'): item for item in data if (item.get('name') or item.get('client_name'))}
        elif isinstance(data, dict):
            # Sometimes agents use name as keys
            data_map = data
        else:
            data_map = {}

        # 3. Calculation Check: Calories (40 points)
        # Alice: 540 (csv) + 405 (txt) = 945
        # Bob: 360
        # Charlie: 450
        # David: 540
        # Eve: 450
        expected_calories = {"Alice": 945, "Bob": 360, "Charlie": 450, "David": 540, "Eve": 450}
        cal_score = 0
        for name, expected in expected_calories.items():
            entry = data_map.get(name)
            if entry:
                # Look for calories field (flexible naming)
                actual = entry.get('total_calories_burned') or entry.get('calories') or entry.get('total_calories')
                if actual and abs(float(actual) - expected) < 1.0:
                    cal_score += 8 # 8 points per correct person
        
        total_score += cal_score
        results.append({"item": "Calorie Calculation Accuracy", "score": cal_score, "max_score": 40, "passed": cal_score == 40, "reason": f"Correctly calculated {cal_score//8}/5 people"})

        # 4. Dietary Filtering: Only RSVP'd (30 points)
        # RSVP True: Alice (Kosher), Charlie (Vegan), David (Gluten-Free)
        # RSVP False: Bob, Eve
        rsvp_yes = ["Alice", "Charlie", "David"]
        rsvp_no = ["Bob", "Eve"]
        
        filter_correct = True
        reason_filter = "Correct filtering"
        
        for name in rsvp_yes:
            entry = data_map.get(name)
            if not entry or ('dietary_restriction' not in entry and 'diet_needs' not in entry):
                filter_correct = False
                reason_filter = f"Missing dietary info for {name}"
                break
            diet = entry.get('dietary_restriction') or entry.get('diet_needs')
            expected_diet = "Kosher" if name == "Alice" else "Vegan" if name == "Charlie" else "Gluten-Free"
            if str(diet).lower() != expected_diet.lower():
                filter_correct = False
                reason_filter = f"Wrong diet for {name}: {diet}"
                break
        
        # Check that Bob and Eve do NOT have diet needs listed (or are not in list if RSVP was the filter)
        for name in rsvp_no:
            entry = data_map.get(name)
            if entry:
                diet = entry.get('dietary_restriction') or entry.get('diet_needs')
                if diet: # If they have diet info but RSVP'd False, it's a fail
                    filter_correct = False
                    reason_filter = f"Should not include diet info for {name} (RSVP False)"
        
        score_4 = 30 if filter_correct else 0
        total_score += score_4
        results.append({"item": "RSVP-based Dietary Filtering", "score": score_4, "max_score": 30, "passed": filter_correct, "reason": reason_filter})

        # 5. Distractor Handling (10 points)
        # Ensure 'CorruptedRow' or empty names are not in the output
        distractor_clean = True
        for key in data_map.keys():
            if key in [None, "", "CorruptedRow", "corrupted data line"]:
                distractor_clean = False
        
        score_5 = 10 if distractor_clean else 0
        total_score += score_5
        results.append({"item": "Data Cleaning (Distractors)", "score": score_5, "max_score": 10, "passed": distractor_clean, "reason": "No corrupted data found" if distractor_clean else "Found corrupted data in output"})

    # Final Summary
    output = {
        "total_score": int(total_score),
        "details": results
    }
    
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    verify()
