import os
import sys
import json
import httpx
from openai import OpenAI

# ==============================================================================
# 强制 API 规范 (LLM 初始化)
# ==============================================================================
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
    """
    LLM 辅助验证非结构化文本内容（如有需要）
    """
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
# 核心检测逻辑
# ==============================================================================
def verify_workspace(workspace):
    details = []
    total_score = 0
    
    report_path = os.path.join(workspace, "deliverables", "festival_report.json")
    
    # 1. 检查文件是否存在 (10分)
    if os.path.exists(report_path):
        details.append({"item": "检查交付物是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "找到了 festival_report.json 文件"})
        total_score += 10
    else:
        details.append({"item": "检查交付物是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 festival_report.json 文件"})
        # 严重错误，直接返回
        return write_score(workspace, total_score, details)

    # 2. 检查 JSON 格式合法性 (10分)
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            report_data = json.load(f)
        details.append({"item": "JSON 格式验证", "score": 10, "max_score": 10, "passed": True, "reason": "文件是合法的 JSON 格式"})
        total_score += 10
    except Exception as e:
        details.append({"item": "JSON 格式验证", "score": 0, "max_score": 10, "passed": False, "reason": f"解析 JSON 失败: {str(e)}"})
        return write_score(workspace, total_score, details)

    # 将 JSON 内容扁平化或转换为字符串便于提取，但尽量用结构化判断
    # 期望的未授权车牌
    expected_unauthorized = {"ID-SN34K", "MT-N0N0", "WY-B4D1"}
    # 期望的菜系统计
    expected_cuisine_counts = {
        "American": 2,
        "Thai": 2,
        "Native American": 2,
        "Italian": 2,
        "Korean": 1
    }

    # 提取未经授权的车牌列表
    # 考虑到 Agent 可能会以不同 key 存放，寻找列表类型的数据
    unauth_plates = set()
    cuisine_counts = {}
    
    for key, value in report_data.items():
        if isinstance(value, list):
            # 假设这是未授权的车牌列表
            unauth_plates.update(str(v).upper() for v in value)
        elif isinstance(value, dict):
            # 假设这是菜系统计
            cuisine_counts = {str(k).title(): int(v) for k, v in value.items() if str(v).isdigit() or isinstance(v, int)}
            
    # 3. 验证未授权车牌 (40分)
    if not unauth_plates:
        # 尝试深度搜索或者 LLM 辅助提取如果结构太深
        pass 
        
    found_unauth = expected_unauthorized.intersection(unauth_plates)
    wrong_unauth = unauth_plates - expected_unauthorized

    unauth_score = 0
    unauth_reason = ""
    if len(found_unauth) == 3 and len(wrong_unauth) == 0:
        unauth_score = 40
        unauth_reason = "完美找出了所有 3 个未授权车牌且没有包含错误车牌"
    elif len(found_unauth) > 0:
        unauth_score = len(found_unauth) * 10
        unauth_reason = f"找出了部分未授权车牌: {found_unauth}。"
        if len(wrong_unauth) > 0:
            unauth_score = max(0, unauth_score - len(wrong_unauth) * 5)
            unauth_reason += f" 但包含了错误车牌: {wrong_unauth}，扣分。"
    else:
        unauth_reason = "未能在 JSON 中提取出正确的未授权车牌列表。"

    details.append({"item": "验证未授权车牌的准确性", "score": unauth_score, "max_score": 40, "passed": (unauth_score == 40), "reason": unauth_reason})
    total_score += unauth_score

    # 4. 验证菜系统计准确性 (40分)
    cuisine_score = 0
    cuisine_reason = []
    
    correct_matches = 0
    for cuisine, expected_count in expected_cuisine_counts.items():
        # 忽略大小写匹配
        matched = False
        for k, v in cuisine_counts.items():
            if cuisine.lower() in k.lower() and v == expected_count:
                correct_matches += 1
                matched = True
                break
        if not matched:
            cuisine_reason.append(f"未找到或 {cuisine} 数量不等于 {expected_count}")

    if correct_matches == len(expected_cuisine_counts) and len(cuisine_counts) == len(expected_cuisine_counts):
        cuisine_score = 40
        cuisine_reason = "菜系统计完全准确无误。"
    else:
        cuisine_score = correct_matches * 8 # 每个匹配正确得8分
        cuisine_reason = f"匹配了 {correct_matches}/5 种菜系。具体错误: " + "; ".join(cuisine_reason)

    details.append({"item": "验证供应商菜系统计结果", "score": cuisine_score, "max_score": 40, "passed": (cuisine_score == 40), "reason": cuisine_reason})
    total_score += cuisine_score

    return write_score(workspace, total_score, details)

def write_score(workspace, total_score, details):
    output = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    return output

if __name__ == "__main__":
    work_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workspace(work_dir)
