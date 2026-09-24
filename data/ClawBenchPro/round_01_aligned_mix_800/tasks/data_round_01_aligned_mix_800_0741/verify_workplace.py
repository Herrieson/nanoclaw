import os
import sys
import json
import csv
import httpx
from openai import OpenAI

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_dir = os.path.join(workspace, "financial_reports")
    json_path = os.path.join(report_dir, "reconciliation_export.json")
    txt_path = os.path.join(report_dir, "flagged_contractors.txt")
    
    score_details = []
    total_score = 0

    # 1. Check directory structure (10 points)
    if os.path.exists(report_dir) and os.path.isdir(report_dir):
        score_details.append({"item": "Directory 'financial_reports' exists", "score": 10, "max_score": 10, "passed": True, "reason": "Directory created successfully."})
        total_score += 10
    else:
        score_details.append({"item": "Directory 'financial_reports' exists", "score": 0, "max_score": 10, "passed": False, "reason": "Directory missing."})

    # 2. Check reconciliation_export.json format and content (50 points)
    # Expected: Smith Builders: 30*50=1500, Jones Electrical: 20*75=1500, Taylor Plumbing: 10*65=650, Apex Roofing: 12*90=1080
    expected_payouts = {
        "Smith Builders": 1500.0,
        "Jones Electrical": 1500.0,
        "Taylor Plumbing": 650.0,
        "Apex Roofing": 1080.0
    }

    if os.path.exists(json_path):
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            # Format check (10 points)
            score_details.append({"item": "JSON format valid", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON file."})
            total_score += 10
            
            # Payout Accuracy (40 points, 10 per contractor)
            match_count = 0
            for name, expected in expected_payouts.items():
                actual = data.get(name)
                # Check for float equality or close enough
                if actual is not None and abs(float(actual) - expected) < 0.01:
                    match_count += 1
                else:
                    score_details.append({"item": f"Payout calculation for {name}", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected {expected}, got {actual}"})
            
            if match_count > 0:
                payout_score = match_count * 10
                score_details.append({"item": "Payout calculation accuracy", "score": payout_score, "max_score": 40, "passed": match_count == 4, "reason": f"Correctly calculated {match_count}/4 contractors."})
                total_score += payout_score
        except Exception as e:
            score_details.append({"item": "JSON parsing", "score": 0, "max_score": 50, "passed": False, "reason": f"Error parsing JSON: {str(e)}"})
    else:
        score_details.append({"item": "reconciliation_export.json exists", "score": 0, "max_score": 50, "passed": False, "reason": "File missing."})

    # 3. Check flagged_contractors.txt (20 points)
    # Expected: Jones Electrical (85 vs 75), Apex Roofing (95 vs 90)
    expected_flagged = ["Jones Electrical", "Apex Roofing"]
    if os.path.exists(txt_path):
        with open(txt_path, 'r') as f:
            content = f.read()
        
        found_flags = []
        for contractor in expected_flagged:
            if contractor.lower() in content.lower():
                found_flags.append(contractor)
        
        if len(found_flags) == 2:
            score_details.append({"item": "Identify overbilling contractors", "score": 20, "max_score": 20, "passed": True, "reason": "Correctly identified both overbilling contractors."})
            total_score += 20
        elif len(found_flags) == 1:
            score_details.append({"item": "Identify overbilling contractors", "score": 10, "max_score": 20, "passed": False, "reason": f"Only identified {found_flags[0]}."})
            total_score += 10
        else:
            score_details.append({"item": "Identify overbilling contractors", "score": 0, "max_score": 20, "passed": False, "reason": "Failed to identify overbilling contractors."})
    else:
        score_details.append({"item": "flagged_contractors.txt exists", "score": 0, "max_score": 20, "passed": False, "reason": "File missing."})

    # 4. LLM Verification for Strict Adherence to instructions (20 points)
    # We check if there are extra contractors who shouldn't be flagged or if the JSON contains unauthorized rates.
    MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
    MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
    MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

    http_client = httpx.Client(verify=False)
    client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)

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
        except:
            return False

    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            json_str = f.read()
        
        # Audit logic check via LLM: Did the Agent accidentally use the "Billed Rate" from the invoice instead of the "Approved Rate"?
        # Since we already did code check, this is a secondary safety net for hallucination or logic errors.
        prompt = "In the provided JSON, look at 'Jones Electrical'. The correct payout should be 1500 (20 hours * 75 approved rate). If the Agent used the billed rate of 85, it would be 1700. Does the JSON strictly use the approved rates from the contract (75 for Jones, 90 for Apex) for its calculations?"
        is_correct_logic = llm_judge_content(prompt, json_str)
        
        if is_correct_logic:
            score_details.append({"item": "Audit Logic Verification (No use of unauthorized rates)", "score": 20, "max_score": 20, "passed": True, "reason": "Agent correctly used approved rates instead of billed rates."})
            total_score += 20
        else:
            score_details.append({"item": "Audit Logic Verification", "score": 0, "max_score": 20, "passed": False, "reason": "LLM detected use of unauthorized billed rates in calculation."})
    else:
        score_details.append({"item": "Audit Logic Verification", "score": 0, "max_score": 20, "passed": False, "reason": "JSON not available for LLM check."})

    # Final output
    output = {
        "total_score": min(100, total_score),
        "details": score_details
    }
    
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    main()
