import os
import sys
import json
import re
import httpx
from openai import OpenAI

# =====================================================================
# 强制 API 规范 (Mock)
# =====================================================================
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
    """用于自然语言检测的辅助方法（本任务核心数据为结构化，暂作为降级方案保留）"""
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

# =====================================================================
# 核心验证逻辑
# =====================================================================
def write_score(total_score, details):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

def extract_numbers(obj, extracted):
    """递归从 JSON 对象中提取所有可能的数字格式"""
    if isinstance(obj, (int, float)):
        extracted.append(float(obj))
    elif isinstance(obj, str):
        # 尝试清洗货币字符串，例如 "$20,350", "20350.00"
        clean_str = obj.replace("$", "").replace(",", "").strip()
        try:
            extracted.append(float(clean_str))
        except ValueError:
            pass
    elif isinstance(obj, dict):
        for v in obj.values():
            extract_numbers(v, extracted)
    elif isinstance(obj, list):
        for item in obj:
            extract_numbers(item, extracted)

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_dir = os.path.join(workspace, "precinct_desk")
    target_file = os.path.join(target_dir, "bolo_summary.json")
    
    score_details = []
    total_score = 0
    
    # 1. 检查文件是否存在 (10分)
    if os.path.exists(target_file):
        score_details.append({
            "item": "验证目标文件生成", 
            "score": 10, 
            "max_score": 10, 
            "passed": True, 
            "reason": "成功找到了 precinct_desk/bolo_summary.json 结果文件。"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "验证目标文件生成", 
            "score": 0, 
            "max_score": 10, 
            "passed": False, 
            "reason": "未找到要求的 precinct_desk/bolo_summary.json 文件。"
        })
        write_score(0, score_details)
        return

    # 2. 检查 JSON 格式合法性 (10分)
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        score_details.append({
            "item": "验证 JSON 格式", 
            "score": 10, 
            "max_score": 10, 
            "passed": True, 
            "reason": "结果文件是合法的 JSON 格式。"
        })
        total_score += 10
    except Exception as e:
        score_details.append({
            "item": "验证 JSON 格式", 
            "score": 0, 
            "max_score": 10, 
            "passed": False, 
            "reason": f"结果文件 JSON 格式非法，解析失败: {str(e)}"
        })
        write_score(total_score, score_details)
        return
        
    # 3. 验证总财产价值 (40分)
    # 正确总金额 = 4500 (BLY-992) + 12500 (GTA-441) + 850 (LARC-771) + 2200 (ROB-112) + 300 (UNK-909) = 20350
    # 注意：ROB-112 虽然没有颈部纹身，但属于有效事件财产损失，必须计入总额。
    extracted_nums = []
    extract_numbers(data, extracted_nums)
    
    expected_total = 20350.0
    has_correct_total = any(abs(n - expected_total) < 0.1 for n in extracted_nums)
    
    if has_correct_total:
        score_details.append({
            "item": "验证总被盗财产价值计算", 
            "score": 40, 
            "max_score": 40, 
            "passed": True, 
            "reason": "成功提取并计算出了精确的总价值: $20,350。"
        })
        total_score += 40
    else:
        # 检查是否遗漏了某些记录（比如排除了 ROB-112，或者没发现 JSON deep dump 里的项）
        partial_match = False
        reason_str = f"未找到正确总价值 20350。提取到的数字有: {extracted_nums}。"
        if any(abs(n - 18150.0) < 0.1 for n in extracted_nums):
            reason_str += " (诊断: 遗漏了 ROB-112，误将纹身过滤条件应用于了总体财产统计)。"
        elif any(abs(n - 20050.0) < 0.1 for n in extracted_nums):
            reason_str += " (诊断: 遗漏了 deep_scan 目录下的隐藏记录 UNK-909)。"

        score_details.append({
            "item": "验证总被盗财产价值计算", 
            "score": 0, 
            "max_score": 40, 
            "passed": False, 
            "reason": reason_str
        })

    # 4. 验证颈部纹身 ID 列表 (40分)
    # 正确列表: BLY-992, GTA-441, LARC-771, UNK-909
    content_str = json.dumps(data).upper()
    # 使用正则表达式提取大写的案件 ID（兼容诸如大小写混用或字符串拼接的情况）
    found_ids = set(re.findall(r'[A-Z]{3,4}-\d{3,4}', content_str))
    
    target_ids = {"BLY-992", "GTA-441", "LARC-771", "UNK-909"}
    decoy_id = "ROB-112" # 没有颈部纹身的干扰项
    
    intersection = target_ids.intersection(found_ids)
    
    id_score = 0
    id_reason = ""
    
    if len(intersection) == 4:
        id_score += 20
        id_reason += "成功找到了所有 4 个具有颈部纹身嫌疑人的 Case ID。"
        
        # 检查是否包含多余干扰项
        if decoy_id in found_ids:
            id_reason += f" 但未能识别出 '{decoy_id}' 实际上并没有颈部纹身，包含该干扰项扣 20 分。"
        else:
            extra = found_ids - target_ids
            if extra:
                id_score += 10
                id_reason += f" 但包含了系统垃圾中的无效 ID {extra}，扣 10 分。"
            else:
                id_score += 20
                id_reason += " 未包含任何干扰项，条件过滤极其精准，满分。"
    else:
        # 部分命中
        id_score = len(intersection) * 5
        id_reason = f"仅找到部分目标 ID: {intersection}。丢失的正确 ID: {target_ids - found_ids}。"
        if decoy_id in found_ids:
            id_reason += f" 且误包含了不具有颈部纹身的 {decoy_id}。"
            id_score = max(0, id_score - 5)
            
    score_details.append({
        "item": "验证特定嫌疑人 Case ID 提取精准度", 
        "score": id_score, 
        "max_score": 40, 
        "passed": (id_score == 40), 
        "reason": id_reason
    })
    total_score += id_score
    
    write_score(total_score, score_details)

if __name__ == "__main__":
    verify()
