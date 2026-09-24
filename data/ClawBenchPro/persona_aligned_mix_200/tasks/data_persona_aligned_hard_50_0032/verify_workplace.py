import os
import sys
import json
import math
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，强制关闭 SSL 验证
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
                {"role": "user", "content": f"{prompt_text}\n\n[Content]:\n{file_content}"}
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def get_true_energy(step):
    e_base = -1152.0
    if step <= 130:
        return e_base + 100 * math.exp(-step / 30.0)
    else:
        return e_base + math.sin(step) * 0.01

def extract_candidates(data):
    step_candidates = []
    list_candidates = []
    keys_used = []
    
    def traverse(node):
        if isinstance(node, dict):
            for k, v in node.items():
                keys_used.append(str(k))
                traverse(v)
        elif isinstance(node, list):
            if len(node) > 0 and all(isinstance(x, (int, float)) for x in node):
                list_candidates.append(node)
            else:
                for item in node:
                    traverse(item)
        elif isinstance(node, (int, float, str)):
            try:
                val = float(node)
                if val.is_integer() and val > 0:
                    step_candidates.append(int(val))
            except:
                pass
                
    traverse(data)
    return step_candidates, list_candidates, keys_used

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result_path = os.path.join(workspace, "result", "trap_report.json")
    
    total_score = 0
    details = []
    
    # 1. 检查结果文件是否存在及其合法性 (10 分)
    if not os.path.exists(result_path):
        details.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": f"未找到文件: {result_path}"})
        details.append({"item": "字段命名直观性(LLM)", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失，跳过判定。"})
        details.append({"item": "定位被卡死的节点步数", "score": 0, "max_score": 30, "passed": False, "reason": "文件缺失，无法提取。"})
        details.append({"item": "能量序列的数据完整性与精确度", "score": 0, "max_score": 50, "passed": False, "reason": "文件缺失，无法比对。"})
        output_result(0, details)
        return
        
    try:
        with open(result_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        details.append({"item": "检查目标文件是否存在并格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "trap_report.json 存在且 JSON 格式合法。"})
    except Exception as e:
        details.append({"item": "检查目标文件是否存在并格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"文件存在但 JSON 解析失败: {str(e)}"})
        output_result(0, details)
        return

    # 提取所有候选数值和列表
    step_candidates, list_candidates, keys_used = extract_candidates(data)

    # 2. 字段命名语义直观性 - 利用大模型检查 (10 分)
    # 题目要求：“字段名随便你定，只要让我一眼能看出哪一个是卡死的步数、哪一个是能量序列序列就行。”
    if keys_used:
        prompt = "The user requested a JSON format with custom field names. These names must explicitly and intuitively show which field means 'trapped step number / deadlocked step' and which means 'energy sequence / TOTEN list'. Based on the keys below, are they descriptive and intuitive enough?"
        keys_str = ", ".join(list(set(keys_used)))
        is_intuitive = llm_judge_content(prompt, keys_str)
        if is_intuitive:
            details.append({"item": "字段命名直观性(LLM)", "score": 10, "max_score": 10, "passed": True, "reason": f"LLM 判定字段名 [{keys_str}] 直观清晰。"})
            total_score += 10
        else:
            details.append({"item": "字段命名直观性(LLM)", "score": 0, "max_score": 10, "passed": False, "reason": f"LLM 判定字段名 [{keys_str}] 表意不明或包含无意义缩写。"})
    else:
        details.append({"item": "字段命名直观性(LLM)", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 中未提取到有效的键名。"})

    # 3. 定位并提取被卡死的节点步数 (30 分)
    TARGET_STEP = 145
    step_score = 0
    step_reason = "未找到与卡死步数相近或匹配的数值。"
    step_passed = False
    
    if TARGET_STEP in step_candidates:
        step_score = 30
        step_reason = f"精准定位到目标步数 {TARGET_STEP}。"
        step_passed = True
    else:
        # 如果找到了附近的步数，说明算法有少许偏差，给予少量同情分
        closest = min(step_candidates, key=lambda x: abs(x - TARGET_STEP)) if step_candidates else None
        if closest is not None and abs(closest - TARGET_STEP) <= 3:
            step_score = 5
            step_reason = f"定位错误，找到步数 {closest}。算法边界条件判定存在偏差（极差窗口或受力检测出错）。"
        elif step_candidates:
            step_reason = f"找到数值 {step_candidates}，但与目标 {TARGET_STEP} 相去甚远。"

    details.append({"item": "定位被卡死的节点步数", "score": step_score, "max_score": 30, "passed": step_passed, "reason": step_reason})
    total_score += step_score

    # 4. 能量序列的数据完整性与精确度 (50 分)
    true_energies = [get_true_energy(s) for s in range(1, TARGET_STEP + 1)]
    seq_score = 0
    seq_reason = "未找到由数字组成的列表，缺失能量序列数据。"
    seq_passed = False
    
    if list_candidates:
        best_score = 0
        best_reason = ""
        
        for cand in list_candidates:
            match_count = 0
            compare_len = min(len(cand), TARGET_STEP)
            for i in range(compare_len):
                if abs(cand[i] - true_energies[i]) < 1e-3:
                    match_count += 1
                    
            # 基础分按匹配数占比计算
            base_score = (match_count / float(TARGET_STEP)) * 50
            # 长度偏离惩罚
            length_penalty = abs(len(cand) - TARGET_STEP) * 0.5
            final_score = max(0, base_score - length_penalty)
            
            if final_score >= best_score:
                best_score = final_score
                if match_count == TARGET_STEP and len(cand) == TARGET_STEP:
                    best_reason = "能量序列长度完美匹配 (145 步)，且所有数值解析完全精确。"
                elif match_count > 0:
                    best_reason = f"序列长度为 {len(cand)}。提取了部分正确数据，完美匹配 {match_count}/{TARGET_STEP} 项，并进行了长度惩罚。"
                else:
                    best_reason = "找到了列表，但能量数值解析完全不匹配，可能读取了诱饵文件的数据或发生了幻觉。"

        seq_score = int(best_score)
        seq_reason = best_reason
        if seq_score == 50:
            seq_passed = True
            
    details.append({"item": "能量序列的数据完整性与精确度", "score": seq_score, "max_score": 50, "passed": seq_passed, "reason": seq_reason})
    total_score += seq_score
    
    # 最终加上文件分
    total_score += 10
    output_result(total_score, details)

def output_result(total_score, details):
    report = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.setdefault(f, report) # Type Error check
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
