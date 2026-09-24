import os
import sys
import json
import httpx
from openai import OpenAI

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # --- 1. Deliverables Presence (10 points) ---
    crm_path = os.path.join(workspace, "deliverables/ready_for_crm.json")
    volunteer_path = os.path.join(workspace, "deliverables/volunteer_contacts.txt")
    
    if os.path.exists(crm_path):
        score += 5
        details.append({"item": "CRM JSON file exists", "score": 5, "max_score": 5, "passed": True})
    else:
        details.append({"item": "CRM JSON file exists", "score": 0, "max_score": 5, "passed": False})

    if os.path.exists(volunteer_path):
        score += 5
        details.append({"item": "Volunteer TXT file exists", "score": 5, "max_score": 5, "passed": True})
    else:
        details.append({"item": "Volunteer TXT file exists", "score": 0, "max_score": 5, "passed": False})

    # --- 2. CRM Data Content Analysis (50 points) ---
    # Expected Leads: 
    # 01 (TechNova): East, Valid Phone -> YES
    # 04 (South District Retail): South, Invalid Phone format (555-888-9999) -> NO
    # 07 (Eastern Telecom): East, Valid Phone -> YES
    # Others are West, North, or Non-Profit
    expected_crm_companies = ["TechNova Solutions", "Eastern Telecom Partners"]
    rejected_crm_companies = ["South District Retail", "Alpha Logistics", "Global Imports", "Westside Plumbers"]

    if os.path.exists(crm_path):
        try:
            with open(crm_path, 'r', encoding='utf-8') as f:
                crm_data = json.load(f)
            
            if isinstance(crm_data, list):
                found_names = [item.get("Company_Name") or item.get("company") for item in crm_data]
                
                # Check for correct inclusions
                correct_inclusions = sum(1 for name in expected_crm_companies if name in found_names)
                inc_score = (correct_inclusions / len(expected_crm_companies)) * 30
                score += inc_score
                details.append({"item": "CRM Data Accuracy (Inclusion)", "score": int(inc_score), "max_score": 30, "passed": inc_score == 30})

                # Check for incorrect inclusions (Strict phone/district validation)
                incorrect_inclusions = sum(1 for name in rejected_crm_companies if name in found_names)
                dec_score = max(0, 20 - (incorrect_inclusions * 10))
                score += dec_score
                details.append({"item": "CRM Data Precision (Exclusion of invalid leads)", "score": int(dec_score), "max_score": 20, "passed": dec_score == 20})
            else:
                details.append({"item": "CRM Data Format", "score": 0, "max_score": 50, "passed": False, "reason": "JSON is not a list"})
        except Exception as e:
            details.append({"item": "CRM Data Parsing", "score": 0, "max_score": 50, "passed": False, "reason": str(e)})

    # --- 3. Volunteer Contacts Analysis (20 points) ---
    # Expected: 02 (Downtown Soup Kitchen), 06 (Crescent Community Center)
    if os.path.exists(volunteer_path):
        try:
            with open(volunteer_path, 'r', encoding='utf-8') as f:
                vol_content = f.read()
            
            has_soup = "Downtown Soup Kitchen" in vol_content and "help@downtownsoup.org" in vol_content
            has_crescent = "Crescent Community Center" in vol_content and "director@crescentcc.org" in vol_content
            
            vol_score = 0
            if has_soup: vol_score += 10
            if has_crescent: vol_score += 10
            score += vol_score
            details.append({"item": "Volunteer Contact Extraction", "score": vol_score, "max_score": 20, "passed": vol_score == 20})
        except:
            details.append({"item": "Volunteer Data Reading", "score": 0, "max_score": 20, "passed": False})

    # --- 4. LLM Semantic Check: Format & Professionalism (20 points) ---
    if os.path.exists(crm_path) or os.path.exists(volunteer_path):
        MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
        MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
        MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

        try:
            http_client = httpx.Client(verify=False)
            client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)
            
            with open(crm_path if os.path.exists(crm_path) else volunteer_path, 'r') as f:
                sample_content = f.read()[:1000]

            response = client.chat.completions.create(
                model=MOCK_MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are a strict data validation assistant. Answer ONLY with 'YES' or 'NO'."},
                    {"role": "user", "content": f"Does this data look like it was extracted cleanly from a raw source without extraneous conversational text or formatting artifacts?\n\n[Content]:\n{sample_content}"}
                ],
                temperature=0
            )
            if "yes" in response.choices[0].message.content.strip().lower():
                score += 20
                details.append({"item": "LLM: Data Extraction Cleanliness", "score": 20, "max_score": 20, "passed": True})
            else:
                details.append({"item": "LLM: Data Extraction Cleanliness", "score": 0, "max_score": 20, "passed": False, "reason": "Data contains artifacts or messy formatting"})
        except Exception as e:
            details.append({"item": "LLM API Error", "score": 0, "max_score": 20, "passed": False, "reason": str(e)})

    # Final Output
    final_score = min(100, int(score))
    output = {
        "total_score": final_score,
        "details": details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
