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

def extract_ground_truth(workspace):
    log_path = os.path.join(workspace, "var/logs/risk_engine/syslog_20231024.log")
    true_session = None
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                if "CIRCUIT BREAKER ENGAGED. SOURCE:" in line:
                    true_session = line.strip().split("SOURCE: ")[-1].strip()
                    break

    target_t = None
    if true_session:
        session_dir = os.path.join(workspace, "var/data/udp_ingest", true_session)
        if os.path.exists(session_dir):
            files = sorted([f for f in os.listdir(session_dir) if f.startswith("frag_")])
            max_t = -1
            for fname in files:
                with open(os.path.join(session_dir, fname), "r", encoding="utf-8") as f:
                    for line in f:
                        if "ERR_DECODE" in line:
                            continue
                        parts = line.strip().split("\x01")
                        if len(parts) < 4:
                            continue
                        try:
                            t = int(parts[0].strip())
                            if t <= max_t:
                                continue
                            max_t = t
                            bids_str = parts[2].strip()
                            asks_str = parts[3].strip()
                            best_bid = float(bids_str.split("|")[0].split(":")[0])
                            best_ask = float(asks_str.split("|")[0].split(":")[0])
                            if best_bid >= best_ask:
                                target_t = t
                                break
                        except Exception:
                            continue
                if target_t:
                    break
    return target_t, "FAT_FINGER_X"

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0

    target_file = os.path.join(workspace, "ops/target_replay.json")
    
    # Check 1: File Existence (20 pts)
    file_exists = os.path.exists(target_file)
    if file_exists:
        results.append({"item": "检查目标文件是否存在", "score": 20, "max_score": 20, "passed": True, "reason": "文件 ops/target_replay.json 存在"})
        total_score += 20
    else:
        results.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 20, "passed": False, "reason": "未找到 ops/target_replay.json 文件"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": results}, f, ensure_ascii=False, indent=2)
        return

    # Check 2: JSON Structure & Strict Schema (20 pts)
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
            file_content_str = json.dumps(data)
        
        if not isinstance(data, dict):
            raise ValueError("Root is not a JSON object")
        
        if len(data.keys()) > 2:
            results.append({"item": "检查配置是否捏造多余字段", "score": 0, "max_score": 20, "passed": False, "reason": "JSON包含超过2个键，存在严重幻觉或冗余"})
            data_valid = False
        else:
            results.append({"item": "检查配置结构合法性", "score": 20, "max_score": 20, "passed": True, "reason": "JSON格式合法且无冗余字段"})
            total_score += 20
            data_valid = True
            
    except Exception as e:
        results.append({"item": "检查配置结构合法性", "score": 0, "max_score": 20, "passed": False, "reason": f"解析失败或格式错误: {str(e)}"})
        data_valid = False

    if not data_valid:
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": results}, f, ensure_ascii=False, indent=2)
        return

    # Check 3: LLM Semantic Verification for Keys (10 pts)
    keys_str = ", ".join(data.keys())
    llm_prompt = "The user provided JSON keys for a 'symbol' and a 'timestamp'. Are these keys common, clear, and standard English words? Reply YES if they are standard (e.g., 'symbol', 'timestamp', 'time', 'instrument'). Reply NO if they are gibberish, obscure abbreviations, or non-English."
    is_common = llm_judge_content(llm_prompt, keys_str)
    
    if is_common:
        results.append({"item": "利用大模型检查键名语义通俗性", "score": 10, "max_score": 10, "passed": True, "reason": f"键名 [{keys_str}] 被判定为通俗易懂"})
        total_score += 10
    else:
        results.append({"item": "利用大模型检查键名语义通俗性", "score": 0, "max_score": 10, "passed": False, "reason": f"键名 [{keys_str}] 不符合通俗英文规范"})

    # Extract dynamic ground truth
    ground_truth_t, ground_truth_sym = extract_ground_truth(workspace)
    
    # Value extraction heuristics
    extracted_sym = str(list(data.values())[0]) if len(data) > 0 else ""
    extracted_t = str(list(data.values())[1]) if len(data) > 1 else ""
    
    # Correct order logic in case they inverted keys
    for v in data.values():
        if isinstance(v, str) and not v.isdigit():
            extracted_sym = v
        if isinstance(v, (int, float)) or (isinstance(v, str) and v.isdigit()):
            extracted_t = str(v)

    # Check 4: Symbol Extraction (20 pts)
    if extracted_sym == ground_truth_sym:
        results.append({"item": "检查异常 Symbol 解析准确性", "score": 20, "max_score": 20, "passed": True, "reason": f"成功找准异常股票: {ground_truth_sym}"})
        total_score += 20
    else:
        results.append({"item": "检查异常 Symbol 解析准确性", "score": 0, "max_score": 20, "passed": False, "reason": f"Symbol错误，期望值 {ground_truth_sym}，实际包含 {extracted_sym}"})

    # Check 5: Precise Timestamp Calculation (30 pts)
    if ground_truth_t and str(ground_truth_t) == extracted_t:
        results.append({"item": "检查纳秒时间戳的防乱序单调性提取", "score": 30, "max_score": 30, "passed": True, "reason": "严格按时序移除了乱序包，提取到了极其准确的倒挂时间戳"})
        total_score += 30
    else:
        results.append({"item": "检查纳秒时间戳的防乱序单调性提取", "score": 0, "max_score": 30, "passed": False, "reason": f"时间戳不匹配（可能中了乱序废包陷阱），期望值 {ground_truth_t}，实际提取 {extracted_t}"})

    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": results}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
