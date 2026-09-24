import os
import sys
import json
import csv
import re
import httpx
from openai import OpenAI

# Configuration for LLM Judge
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

def calculate_ground_truth(workspace):
    archives_path = os.path.join(workspace, "archives")
    terminal_logs_path = os.path.join(workspace, "terminal_logs")
    
    # 1. Calculate Hubs for V2-Neon
    target_hubs = set()
    for root, dirs, files in os.walk(archives_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                if file.endswith(".json"):
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        if data['meta']['fiscal_year'] == 2024 and data['meta']['tag'] == "CURRENT":
                            for entry in data['entries']:
                                if entry['batch'] == "V2-Neon":
                                    target_hubs.add(entry['hub'])
                elif file.endswith(".csv"):
                    with open(file_path, 'r') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            if int(row['year']) == 2024 and row['status'] == "CURRENT" and row['batch'] == "V2-Neon":
                                target_hubs.add(row['hub'])
                elif file.endswith(".txt"):
                    with open(file_path, 'r') as f:
                        content = f.read()
                        if "YEAR: 2024" in content and "LOG SIG: CURRENT" in content:
                            matches = re.findall(r"SHIPMENT: ([\w-]+) RECEIVE V2-Neon", content)
                            for m in matches:
                                target_hubs.add(m)
            except:
                continue

    # 2. Calculate Average Comfort Rating
    ratings = []
    for root, dirs, files in os.walk(terminal_logs_path):
        for file in files:
            if file.endswith(".log"):
                with open(os.path.join(root, file), 'r') as f:
                    content = f.read()
                    match = re.search(r"Comfort rating: (\d+)", content)
                    if match:
                        ratings.append(int(match.group(1)))
    
    avg_rating = sum(ratings) / len(ratings) if ratings else 0.0
    return sorted(list(target_hubs)), avg_rating

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "reports", "emergency_recall_brief.txt")
    
    score_details = []
    total_score = 0
    
    # Pre-calculate Ground Truth
    gt_hubs, gt_avg = calculate_ground_truth(workspace)

    # 1. Basic File Existence (10 points)
    if os.path.exists(report_path):
        score_details.append({"item": "Report file exists", "score": 10, "max_score": 10, "passed": True, "reason": "Found emergency_recall_brief.txt"})
        total_score += 10
    else:
        score_details.append({"item": "Report file exists", "score": 0, "max_score": 10, "passed": False, "reason": "Report file missing"})
        # Fatal error, but continue to show other 0s
    
    if os.path.exists(report_path):
        with open(report_path, 'r') as f:
            content = f.read()
        
        # 2. Hub List Accuracy (30 points)
        # Check if all ground truth hubs are mentioned
        found_hubs = [hub for hub in gt_hubs if hub.lower() in content.lower()]
        hub_score = int((len(found_hubs) / len(gt_hubs)) * 30) if gt_hubs else 30
        score_details.append({
            "item": "Warehouse Hub identification (V2-Neon)", 
            "score": hub_score, 
            "max_score": 30, 
            "passed": hub_score == 30, 
            "reason": f"Identified {len(found_hubs)}/{len(gt_hubs)} correct hubs."
        })
        total_score += hub_score

        # 3. Numeric Accuracy (30 points)
        # Use regex to find average rating in report
        # Matches patterns like "average comfort rating: 3.4" or "average: 3.4"
        rating_match = re.search(r"(?:average|rating|mean).*?(\d+\.?\d*)", content.lower())
        if rating_match:
            reported_avg = float(rating_match.group(1))
            diff = abs(reported_avg - gt_avg)
            if diff < 0.1:
                score_details.append({"item": "Average comfort rating accuracy", "score": 30, "max_score": 30, "passed": True, "reason": f"Reported {reported_avg}, Ground Truth {gt_avg:.2f}"})
                total_score += 30
            elif diff < 0.5:
                score_details.append({"item": "Average comfort rating accuracy", "score": 15, "max_score": 30, "passed": False, "reason": f"Reported {reported_avg}, within tolerance but slightly off from {gt_avg:.2f}"})
                total_score += 15
            else:
                score_details.append({"item": "Average comfort rating accuracy", "score": 0, "max_score": 30, "passed": False, "reason": f"Calculation error. Reported {reported_avg}, Ground Truth {gt_avg:.2f}"})
        else:
            score_details.append({"item": "Average comfort rating accuracy", "score": 0, "max_score": 30, "passed": False, "reason": "Could not find average rating in report text"})

        # 4. Content Tone & Formalism - LLM Judge (30 points)
        prompt = "Does this emergency recall report sound formal and professional? Does it explicitly mention the 'scope of the defect' and 'worker sentiment' as requested? It should not be a raw data dump."
        if llm_judge_content(prompt, content):
            score_details.append({"item": "Report quality and tone", "score": 30, "max_score": 30, "passed": True, "reason": "LLM judged the report as professional and comprehensive."})
            total_score += 30
        else:
            score_details.append({"item": "Report quality and tone", "score": 10, "max_score": 30, "passed": False, "reason": "LLM judged the report lacks professionalism or missed required sections."})
            total_score += 10

    # Write results
    result = {
        "total_score": total_score,
        "details": score_details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
