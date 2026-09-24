import os
import sys
import json
import httpx
from openai import OpenAI

# Configuration for potential LLM usage
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
    score = 0
    details = []
    
    output_path = os.path.join(workspace, "analysis/valid_p300_peaks.json")
    
    # 1. Check file existence (10 points)
    if os.path.exists(output_path):
        score += 10
        details.append({"item": "Output file existence", "score": 10, "max_score": 10, "passed": True, "reason": "Found analysis/valid_p300_peaks.json"})
        
        # 2. JSON Validity & Structure (10 points)
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                data = json.loads(content)
            score += 10
            details.append({"item": "JSON validity", "score": 10, "max_score": 10, "passed": True, "reason": "File is valid JSON"})
            
            # 3. Precision Check: EVT_001 (25 points)
            # Expected: 14.5
            if "EVT_001" in data and abs(float(data["EVT_001"]) - 14.5) < 0.01:
                score += 25
                details.append({"item": "EVT_001 Correctness", "score": 25, "max_score": 25, "passed": True, "reason": "Correct peak (14.5) for EVT_001"})
            else:
                details.append({"item": "EVT_001 Correctness", "score": 0, "max_score": 25, "passed": False, "reason": f"Expected 14.5, got {data.get('EVT_001')}"})

            # 4. Precision Check: EVT_005 (25 points)
            # Expected: 18.2
            if "EVT_005" in data and abs(float(data["EVT_005"]) - 18.2) < 0.01:
                score += 25
                details.append({"item": "EVT_005 Correctness", "score": 25, "max_score": 25, "passed": True, "reason": "Correct peak (18.2) for EVT_005"})
            else:
                details.append({"item": "EVT_005 Correctness", "score": 0, "max_score": 25, "passed": False, "reason": f"Expected 18.2, got {data.get('EVT_005')}"})

            # 5. Artifact Rejection: EVT_003 and EVT_004 (20 points total)
            # EVT_003 has FZ artifact, EVT_004 has CZ artifact.
            rejected_003 = "EVT_003" not in data
            rejected_004 = "EVT_004" not in data
            
            if rejected_003:
                score += 10
                details.append({"item": "Artifact Rejection (FZ)", "score": 10, "max_score": 10, "passed": True, "reason": "Correctly rejected EVT_003 due to FZ spike"})
            else:
                details.append({"item": "Artifact Rejection (FZ)", "score": 0, "max_score": 10, "passed": False, "reason": "Failed to reject EVT_003 (FZ artifact)"})
                
            if rejected_004:
                score += 10
                details.append({"item": "Artifact Rejection (CZ)", "score": 10, "max_score": 10, "passed": True, "reason": "Correctly rejected EVT_004 due to CZ spike"})
            else:
                details.append({"item": "Artifact Rejection (CZ)", "score": 0, "max_score": 10, "passed": False, "reason": "Failed to reject EVT_004 (CZ artifact)"})

            # 6. Type Filtering: EVT_002 (10 points)
            # EVT_002 is N200, should be ignored.
            if "EVT_002" not in data:
                score += 10
                details.append({"item": "Target Type Filtering", "score": 10, "max_score": 10, "passed": True, "reason": "Correctly ignored non-P300 stimulus EVT_002"})
            else:
                details.append({"item": "Target Type Filtering", "score": 0, "max_score": 10, "passed": False, "reason": "Failed to filter out non-P300 stimulus"})

            # Bonus/Cleanup: No extra verbosity check (LLM)
            # The prompt requested NO code explanations in the output.
            is_clean = llm_judge_content("Does the provided JSON file contain ONLY the stimulus-to-peak-voltage mapping without any conversational filler, explanations, or code commentary?", content)
            if not is_clean:
                penalty = 10
                score = max(0, score - penalty)
                details.append({"item": "Output Cleanliness", "score": -penalty, "max_score": 0, "passed": False, "reason": "Output contained forbidden explanations or commentary"})

        except Exception as e:
            details.append({"item": "JSON Parsing", "score": 0, "max_score": 10, "passed": False, "reason": f"Error parsing JSON: {str(e)}"})
    else:
        details.append({"item": "Output file existence", "score": 0, "max_score": 100, "passed": False, "reason": "analysis/valid_p300_peaks.json not found"})

    # Ensure score is integer and capped
    final_score = min(100, max(0, int(score)))
    
    result = {
        "total_score": final_score,
        "details": details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
