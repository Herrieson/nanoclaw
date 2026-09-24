import os
import sys
import json
import httpx
import re
import csv
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

def calculate_ground_truth(workspace):
    base_dir = os.path.join(workspace, "garage_dump")
    crew = {}
    parts_to_order = set()
    noise_parts = set()
    
    # 遍历获取 Truth
    for root, _, files in os.walk(base_dir):
        for f in files:
            file_path = os.path.join(root, f)
            # 1. 找人员名单
            if f == "system_config_v2.cfg":
                with open(file_path, 'r', encoding='utf-8') as file:
                    for line in file:
                        if line.startswith("ENTRY:"):
                            parts = line.strip()[6:].split("|")
                            if len(parts) == 2:
                                crew[parts[0]] = {"name": parts[1], "hours": 0.0}

            # 2. 找零件数据
            elif f.startswith("data_blob_") and f.endswith(".csv"):
                with open(file_path, 'r', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    header = next(reader, None)
                    if header and "part_name" in header:
                        for row in reader:
                            if len(row) >= 4:
                                part, stock, status, date = row[0], float(row[1]), row[2], row[3]
                                if status == "verified" and date.startswith("2023-10"):
                                    if stock < 5:
                                        parts_to_order.add(part.lower())
                                    else:
                                        noise_parts.add(part.lower())
                                else:
                                    noise_parts.add(part.lower())

    # 3. 计算工时
    for root, _, files in os.walk(base_dir):
        for f in files:
            file_path = os.path.join(root, f)
            if f.startswith("log_delta_") and f.endswith(".json"):
                with open(file_path, 'r', encoding='utf-8') as file:
                    try:
                        data = json.load(file)
                        w_id = data.get("worker_id")
                        if w_id in crew:
                            crew[w_id]["hours"] += float(data.get("hours_logged", 0.0))
                    except: pass
            elif f.startswith("fragment_") and f.endswith(".tmp"):
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    w_match = re.search(r"WORKER_ID:\s*(V-\d{4})", content)
                    h_match = re.search(r"HOURS:\s*([\d\.]+)", content)
                    if w_match and h_match:
                        w_id = w_match.group(1)
                        if w_id in crew:
                            crew[w_id]["hours"] += float(h_match.group(1))

    return crew, parts_to_order, noise_parts

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliv_dir = os.path.join(workspace, "deliverables")
    
    details = []
    total_score = 0
    
    # 1. 检查交付物目录 (10 pts)
    if not os.path.exists(deliv_dir) or not os.path.isdir(deliv_dir):
        details.append({"item": "Deliverables Directory", "score": 0, "max_score": 10, "passed": False, "reason": "deliverables directory not found."})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": details}, f)
        return
    else:
        details.append({"item": "Deliverables Directory", "score": 10, "max_score": 10, "passed": True, "reason": "deliverables directory exists."})
        total_score += 10

    # 读取所有生成内容，进行联合校验
    all_content = ""
    for f in os.listdir(deliv_dir):
        fpath = os.path.join(deliv_dir, f)
        if os.path.isfile(fpath):
            try:
                with open(fpath, 'r', encoding='utf-8') as file:
                    all_content += file.read() + "\n"
            except: pass
    
    all_content_lower = all_content.lower()
    crew, truth_parts, noise_parts = calculate_ground_truth(workspace)

    # 2. 验证 Parts Order (40 pts)
    # 正确找齐零件 (20 pts)
    parts_found = 0
    for p in truth_parts:
        if p in all_content_lower:
            parts_found += 1
    
    if len(truth_parts) > 0:
        parts_score = int(20 * (parts_found / len(truth_parts)))
    else:
        parts_score = 0
        
    details.append({
        "item": "Identify required parts (<5, verified, Oct 2023)", 
        "score": parts_score, 
        "max_score": 20, 
        "passed": parts_score == 20, 
        "reason": f"Found {parts_found}/{len(truth_parts)} true parts."
    })
    total_score += parts_score

    # 排除干扰/错误零件 (20 pts)
    noise_penalty = 0
    for p in noise_parts:
        if p in all_content_lower:
            noise_penalty += 10
    
    exclusion_score = max(0, 20 - noise_penalty)
    details.append({
        "item": "Exclude invalid/outdated parts", 
        "score": exclusion_score, 
        "max_score": 20, 
        "passed": exclusion_score == 20, 
        "reason": f"Penalty for including {noise_penalty//10} noise parts."
    })
    total_score += exclusion_score

    # 3. 验证 Volunteer Hours (40 pts)
    hours_score = 0
    crew_details = []
    if not crew:
        crew_details.append("No official crew found in truth.")
    else:
        pts_per_member = 40 / len(crew)
        for w_id, info in crew.items():
            name = info["name"]
            expected_h = info["hours"]
            # 用正则查找人名附近（如整段文本或紧接着的数字）的数字
            # 为了容错，匹配人名及前后50字符内的浮点数
            pattern = re.compile(rf"{re.escape(name)}[\s\S]{{0,50}}?(\d+\.\d+|\d+)", re.IGNORECASE)
            match = pattern.search(all_content)
            if match:
                found_h = float(match.group(1))
                if abs(found_h - expected_h) < 0.2:
                    hours_score += pts_per_member
                    crew_details.append(f"{name}: Match ({expected_h})")
                else:
                    crew_details.append(f"{name}: Value mismatch (Expected {expected_h}, Found {found_h})")
            else:
                crew_details.append(f"{name}: Not found")

    hours_score = int(hours_score)
    details.append({
        "item": "Calculate correct hours for official crew",
        "score": hours_score,
        "max_score": 40,
        "passed": hours_score == 40,
        "reason": ", ".join(crew_details)
    })
    total_score += hours_score

    # 4. LLM 语义校验 (10 pts)
    llm_prompt = "Check if the document contains two distinct, readable sections or reports: one for Parts to Order and one for Volunteer Hours. Does it look like a formal summary report rather than raw code dumps?"
    is_valid_format = llm_judge_content(llm_prompt, all_content[:2000]) # 限制长度防止超长
    
    if is_valid_format:
        details.append({"item": "LLM Semantic Check", "score": 10, "max_score": 10, "passed": True, "reason": "Passed formal report structure check."})
        total_score += 10
    else:
        details.append({"item": "LLM Semantic Check", "score": 0, "max_score": 10, "passed": False, "reason": "Failed formal report structure check."})

    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    main()
