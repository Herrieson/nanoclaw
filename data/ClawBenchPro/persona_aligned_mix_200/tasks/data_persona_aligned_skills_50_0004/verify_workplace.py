import os
import sys
import json
import re
import httpx
from openai import OpenAI

# ==============================================================================
# 强制 API 规范初始化 (LLM 探针)
# ==============================================================================
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，必须关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """用于检测非结构化文本语义的统一接口"""
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

# ==============================================================================
# 核心检测逻辑 (代码 + LLM 混合探针)
# ==============================================================================
def evaluate(workspace):
    score_details = []
    total_score = 0
    
    ghost_ids_file = os.path.join(workspace, "calibration", "ghost_ids.txt")
    
    # --- 1. 检查工作目录与目标文件是否存在 (10 分) ---
    if os.path.exists(ghost_ids_file):
        score_details.append({
            "item": "检查目标文件 ghost_ids.txt 是否存在", 
            "score": 10, "max_score": 10, "passed": True, 
            "reason": "目标文件存在"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "检查目标文件 ghost_ids.txt 是否存在", 
            "score": 0, "max_score": 10, "passed": False, 
            "reason": "未找到 calibration/ghost_ids.txt"
        })
        write_score(workspace, total_score, score_details)
        return

    # 读取文件内容
    try:
        with open(ghost_ids_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
    except Exception as e:
        score_details.append({
            "item": "尝试读取文件内容", 
            "score": 0, "max_score": 10, "passed": False, 
            "reason": f"文件读取失败: {e}"
        })
        write_score(workspace, total_score, score_details)
        return

    # --- 2. 语义检查：严格的无冗余约束 (10 分) ---
    # 业务要求严禁长篇大论，只接受极简输出
    prompt = """
    The user was commanded to ONLY write a comma-separated list of Object IDs to the file, and NOTHING else. 
    Strictly check the provided file content. 
    Does it cleanly contain ONLY numbers and basic punctuation (like commas and spaces)? 
    If it contains conversational filler, paragraph-long explanations, or report-style text, output NO.
    If it strictly follows the minimalist constraint, output YES.
    """
    is_clean = llm_judge_content(prompt, content)
    if is_clean:
        score_details.append({
            "item": "利用大模型检查内容是否遵从极简指令", 
            "score": 10, "max_score": 10, "passed": True, 
            "reason": "大模型判定文件内容未包含任何冗长废话，遵循指令"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "利用大模型检查内容是否遵从极简指令", 
            "score": 0, "max_score": 10, "passed": False, 
            "reason": "大模型判定文件中存在违规的长篇大论或分析报告，未遵循极简指令"
        })

    # --- 3. 确定性解析：高精度的召回率与误报检验 ---
    # 使用正则表达式提取所有出现的数字（以规避 Agent 可能使用非标点符号包裹的情况）
    nums = re.findall(r'\d+', content)
    extracted_ids = set(int(x) for x in nums)
    
    # 理论上的正确 Ghost ID 集合 (推导: ID 18 置信度0.45; ID 27 时差80ms; ID 42 置信度0.5&时差80ms; ID 68 时差51ms)
    expected_ids = {18, 27, 42, 68}
    
    # a. 漏报检查 (满分 60 分，每个 ID 分配 15 分)
    for eid in expected_ids:
        if eid in extracted_ids:
            score_details.append({
                "item": f"精准召回：提取幽灵目标 ID {eid}", 
                "score": 15, "max_score": 15, "passed": True, 
                "reason": f"成功识别并输出异常目标 {eid}"
            })
            total_score += 15
        else:
            score_details.append({
                "item": f"精准召回：提取幽灵目标 ID {eid}", 
                "score": 0, "max_score": 15, "passed": False, 
                "reason": f"遗漏了异常目标 {eid}"
            })

    # b. 误报与幻觉检查 (满分 20 分)
    false_positives = extracted_ids - expected_ids
    if len(false_positives) == 0:
        score_details.append({
            "item": "幻觉与干扰项隔离：确保无误报", 
            "score": 20, "max_score": 20, "passed": True, 
            "reason": "干净纯粹，没有捏造或误判其他正常目标 ID"
        })
        total_score += 20
    else:
        penalty = len(false_positives) * 10
        earned = max(0, 20 - penalty)
        score_details.append({
            "item": "幻觉与干扰项隔离：确保无误报", 
            "score": earned, "max_score": 20, "passed": earned == 20, 
            "reason": f"存在 {len(false_positives)} 个误报 ID {list(false_positives)}。每个误报扣减10分，此项最终得分 {earned}"
        })
        total_score += earned

    write_score(workspace, total_score, score_details)

def write_score(workspace, total_score, score_details):
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": score_details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    workspace_path = sys.argv[1] if len(sys.argv) > 1 else "."
    evaluate(workspace_path)
