import os
import sys
import json
import csv
import httpx
from openai import OpenAI

# -----------------------------------------------------------------------------
# Configuration & Constants
# -----------------------------------------------------------------------------
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Initialize LLM Client
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """Unified interface for LLM validation of non-structured text."""
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

# -----------------------------------------------------------------------------
# Scoring Logic
# -----------------------------------------------------------------------------
def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_dir = os.path.join(workspace, "deliverables")
    score_details = []

    # 1. Directory Structure (10 points)
    dir_exists = os.path.exists(deliverables_dir) and os.path.isdir(deliverables_dir)
    score_details.append({
        "item": "Check deliverables folder existence",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "Folder 'deliverables' found." if dir_exists else "Folder 'deliverables' not found."
    })

    if not dir_exists:
        # Cannot proceed reliably without the target folder
        finalize_score(score_details)
        return

    # 2. Find Recommendation File
    files = [f for f in os.listdir(deliverables_dir) if os.path.isfile(os.path.join(deliverables_dir, f))]
    rec_file = files[0] if files else None
    
    if not rec_file:
        score_details.append({"item": "Check recommendation file existence", "score": 0, "max_score": 30, "passed": False, "reason": "No files found in deliverables."})
        finalize_score(score_details)
        return

    file_path = os.path.join(deliverables_dir, rec_file)
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 3. Content Accuracy - Blacklist Check (30 points)
    # BioTech_Bob is blacklisted. He must NOT be in the shortlist.
    not_blacklisted = "biotech_bob" not in content.lower()
    score_details.append({
        "item": "Exclusion of blacklisted influencers",
        "score": 30 if not_blacklisted else 0,
        "max_score": 30,
        "passed": not_blacklisted,
        "reason": "BioTech_Bob correctly excluded." if not_blacklisted else "BioTech_Bob (blacklisted) was found in recommendations."
    })

    # 4. Content Accuracy - Calculation & Top 3 Ranking (40 points)
    # Expected scores (Impact = Likes + 5*Comm + 10*Shares):
    # Derma_Diana: 1500 + 500 + 500 = 2500 (Rank 1)
    # Chemistry_Chloe: 2000 + 50 + 50 = 2100 (Rank 2)
    # Aria_Style: 1000 + 250 + 100 = 1350 (Rank 3)
    # Elegant_Eve: 500 + 100 + 20 = 620 (Rank 4)
    # BioTech_Bob: 60000 (Blacklisted)
    
    ranking_correct = ("derma_diana" in content.lower() and 
                       "chemistry_chloe" in content.lower() and 
                       "aria_style" in content.lower())
    
    score_details.append({
        "item": "Shortlist accuracy (Top 3 correct based on scoring logic)",
        "score": 40 if ranking_correct else 0,
        "max_score": 40,
        "passed": ranking_correct,
        "reason": "Top 3 (Diana, Chloe, Aria) correctly identified." if ranking_correct else "Top 3 identification failed or calculation incorrect."
    })

    # 5. Semantic Professionalism - LLM Judge (20 points)
    # User is stressed/busy - check if the result is concise and professional.
    prompt = "The user is a busy executive. Does this file provide a clear, definitive shortlist of the top 3 influencers without unnecessary fluff? Answer 'YES' if it is concise and professional."
    is_professional = llm_judge_content(prompt, content)
    score_details.append({
        "item": "Professionalism and Conciseness",
        "score": 20 if is_professional else 0,
        "max_score": 20,
        "passed": is_professional,
        "reason": "LLM judged content as professional and clear." if is_professional else "Content judged as wordy or unprofessional."
    })

    finalize_score(score_details)

def finalize_score(details):
    total_score = sum(d["score"] for d in details)
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
