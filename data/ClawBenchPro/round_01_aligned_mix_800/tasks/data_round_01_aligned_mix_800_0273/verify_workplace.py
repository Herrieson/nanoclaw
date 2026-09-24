import os
import sys
import json
import httpx
from openai import OpenAI

# Environment setup
workspace = sys.argv[1] if len(sys.argv) > 1 else "."
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
    score_details = []
    total_score = 0
    target_path = os.path.join(workspace, "plans/budget_and_materials_summary.json")

    # 1. File Existence and Structure (10 points)
    if os.path.exists(target_path):
        score_details.append({"item": "File Existence", "score": 10, "max_score": 10, "passed": True, "reason": "Target file exists."})
        total_score += 10
        try:
            with open(target_path, 'r') as f:
                data = json.load(f)
            score_details.append({"item": "JSON Validity", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON format."})
            total_score += 10
        except:
            score_details.append({"item": "JSON Validity", "score": 0, "max_score": 10, "passed": False, "reason": "Invalid JSON format."})
            data = {}
    else:
        score_details.append({"item": "File Existence", "score": 0, "max_score": 10, "passed": False, "reason": "Target file not found."})
        data = {}

    # 2. Outdoor Expenses Calculation (40 points)
    # Expected: 
    # Hiking: 120.50 (Jan) + 15.25 (Feb) = 135.75
    # Camping: 85.00 (Jan) + 40.00 (Feb) = 125.00
    # Total: 260.75
    outdoor_total = data.get("total_outdoor_expenses", 0)
    try:
        # We allow a small float delta
        if abs(float(outdoor_total) - 260.75) < 0.01:
            score_details.append({"item": "Outdoor Expenses Math", "score": 40, "max_score": 40, "passed": True, "reason": "Correctly aggregated Jan and Feb hiking/camping costs."})
            total_score += 40
        elif abs(float(outdoor_total) - 205.50) < 0.01:
            score_details.append({"item": "Outdoor Expenses Math", "score": 20, "max_score": 40, "passed": False, "reason": "Only Jan data found; failed to process Feb OCR data."})
            total_score += 20
        else:
            score_details.append({"item": "Outdoor Expenses Math", "score": 0, "max_score": 40, "passed": False, "reason": f"Incorrect total: {outdoor_total}. Expected 260.75."})
    except:
        score_details.append({"item": "Outdoor Expenses Math", "score": 0, "max_score": 40, "passed": False, "reason": "Total expenses not a valid number."})

    # 3. Wood Inventory Calculation (30 points)
    # Shed: Oak (4, Usable), Cedar (2, Usable). Pine (6, Moisture 22% -> Unusable)
    # Porch: Pine (5, Usable), Maple (1, Usable). Oak (2, Fungi D -> Unusable)
    # Expected Summary: Oak: 4, Cedar: 2, Pine: 5, Maple: 1
    usable_counts = data.get("usable_boards_by_type", {})
    expected_boards = {"Oak": 4, "Cedar": 2, "Pine": 5, "Maple": 1}
    
    match_count = 0
    for wood, count in expected_boards.items():
        if usable_counts.get(wood) == count:
            match_count += 1
            
    if match_count == 4:
        score_details.append({"item": "Wood Quality Analysis", "score": 30, "max_score": 30, "passed": True, "reason": "Correctly filtered wood using moisture/fungi criteria via tool."})
        total_score += 30
    elif match_count > 0:
        p_score = match_count * 5
        score_details.append({"item": "Wood Quality Analysis", "score": p_score, "max_score": 30, "passed": False, "reason": f"Partial match: {match_count}/4 wood types correct."})
        total_score += p_score
    else:
        score_details.append({"item": "Wood Quality Analysis", "score": 0, "max_score": 30, "passed": False, "reason": "Wood counts are entirely missing or incorrect."})

    # 4. LLM Verification for Tone and Completeness (10 points)
    # The prompt asked to be 'straight' and helpful for an anxious user.
    with open(target_path, 'r') as f:
        file_text = f.read()
    
    is_supportive = llm_judge_content(
        "Does this JSON file or accompanying structure provide a clear, empathetic but direct summary suitable for a grieving carpenter? Check if it specifically lists both outdoor costs and wood counts.",
        file_text
    )
    if is_supportive:
        score_details.append({"item": "Communication & Tone", "score": 10, "max_score": 10, "passed": True, "reason": "Summary is clear and follows user's specific output instructions."})
        total_score += 10
    else:
        score_details.append({"item": "Communication & Tone", "score": 0, "max_score": 10, "passed": False, "reason": "LLM judged the output as unclear or missing requested sections."})

    # Final Output
    final_result = {
        "total_score": int(total_score),
        "details": score_details
    }
    
    with open("workplace_score.json", "w") as f:
        json.dump(final_result, f, indent=2)

if __name__ == "__main__":
    verify()
