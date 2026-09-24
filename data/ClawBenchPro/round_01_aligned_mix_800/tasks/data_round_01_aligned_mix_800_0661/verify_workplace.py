import os
import sys
import json
import httpx
import re
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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    clean_route_dir = os.path.join(workspace, "clean_route")
    
    score_details = []
    total_score = 0
    
    # Target Data
    zone_7_vips = ["TRK-7771", "TRK-7772"]
    zone_7_stds = ["TRK-7001", "TRK-7002", "TRK-7003"]
    out_of_zones = ["TRK-3001", "TRK-9001", "TRK-3002"]

    # 1. 检查目录是否存在 (10分)
    if os.path.isdir(clean_route_dir):
        score_details.append({"item": "Check if 'clean_route' directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Directory exists."})
        total_score += 10
    else:
        score_details.append({"item": "Check if 'clean_route' directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "Directory does not exist."})
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": 0, "details": score_details}, f, indent=4)
        return

    files_in_dir = os.listdir(clean_route_dir)
    if not files_in_dir:
        score_details.append({"item": "Check if files exist in 'clean_route'", "score": 0, "max_score": 90, "passed": False, "reason": "Directory is empty."})
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=4)
        return
        
    route_file_content = ""
    out_file_content = ""
    
    # Attempt to classify files based on their content
    for fname in files_in_dir:
        fpath = os.path.join(clean_route_dir, fname)
        if not os.path.isfile(fpath): continue
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            if all(trk in content for trk in zone_7_vips + zone_7_stds):
                route_file_content = content
            if all(trk in content for trk in out_of_zones):
                out_file_content = content

    # 2. 检查 Zone 7 路线文件及完整性 (20分)
    if route_file_content:
        # 确保里面没有混入 out-of-zone
        if any(trk in route_file_content for trk in out_of_zones):
            score_details.append({"item": "Zone 7 Route completeness and purity", "score": 5, "max_score": 20, "passed": False, "reason": "Found out-of-zone tracking numbers in the route file."})
            total_score += 5
        else:
            score_details.append({"item": "Zone 7 Route completeness and purity", "score": 20, "max_score": 20, "passed": True, "reason": "All Zone 7 packages included, out-of-zone excluded."})
            total_score += 20
    else:
        score_details.append({"item": "Zone 7 Route completeness and purity", "score": 0, "max_score": 20, "passed": False, "reason": "Could not find a file containing all Zone 7 tracking numbers."})

    # 3. 检查 VIP 排序优先级 (30分)
    if route_file_content:
        max_vip_idx = max(route_file_content.find(trk) for trk in zone_7_vips)
        min_std_idx = min(route_file_content.find(trk) for trk in zone_7_stds if route_file_content.find(trk) != -1)
        
        if max_vip_idx != -1 and min_std_idx != -1 and max_vip_idx < min_std_idx:
            score_details.append({"item": "VIP priority sorting", "score": 30, "max_score": 30, "passed": True, "reason": "VIP packages appear before standard packages."})
            total_score += 30
        else:
            score_details.append({"item": "VIP priority sorting", "score": 0, "max_score": 30, "passed": False, "reason": "VIP packages are not correctly prioritized at the top."})
    else:
         score_details.append({"item": "VIP priority sorting", "score": 0, "max_score": 30, "passed": False, "reason": "Missing route file to evaluate sorting."})

    # 4. 检查 Out-of-zone 列表文件及完整性 (20分)
    if out_file_content:
        if any(trk in out_file_content for trk in zone_7_vips + zone_7_stds):
            score_details.append({"item": "Out-of-zone list completeness and purity", "score": 10, "max_score": 20, "passed": False, "reason": "Found Zone 7 tracking numbers in the out-of-zone list."})
            total_score += 10
        else:
            score_details.append({"item": "Out-of-zone list completeness and purity", "score": 20, "max_score": 20, "passed": True, "reason": "All out-of-zone packages included securely."})
            total_score += 20
    else:
        score_details.append({"item": "Out-of-zone list completeness and purity", "score": 0, "max_score": 20, "passed": False, "reason": "Could not find a file containing out-of-zone tracking numbers."})

    # 5. LLM 判断 Out-of-zone 文件格式是否干净 (20分)
    if out_file_content:
        prompt = "Does the following text contain ONLY a clean list of tracking numbers (with optional minimal headers like 'Tracking Numbers'), without detailed addresses or routing details for each?"
        is_clean = llm_judge_content(prompt, out_file_content)
        if is_clean:
            score_details.append({"item": "Clean formatting for out-of-zone list", "score": 20, "max_score": 20, "passed": True, "reason": "LLM verified the list is a clean list of tracking numbers."})
            total_score += 20
        else:
            score_details.append({"item": "Clean formatting for out-of-zone list", "score": 5, "max_score": 20, "passed": False, "reason": "LLM judged the list as not being a separate clean list of just tracking numbers."})
            total_score += 5
    else:
        score_details.append({"item": "Clean formatting for out-of-zone list", "score": 0, "max_score": 20, "passed": False, "reason": "Missing out-of-zone list."})

    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": score_details
        }, f, indent=4)

if __name__ == "__main__":
    main()
