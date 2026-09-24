import os
import sys
import json
import re
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
    """
    统一的非结构化语义检测接口，调用大模型判定
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

def extract_number(val):
    """从可能包含文本的数值中安全提取整数 (例如 '13 hours' -> 13)"""
    if val is None or val == "":
        return None
    m = re.search(r'\d+', str(val))
    return int(m.group()) if m else None

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    board_dir = os.path.join(workspace, "board_submission")
    
    # Check 1: 工作区目录是否存在 (10 分)
    if os.path.isdir(board_dir):
        total_score += 10
        score_details.append({"item": "检查目标输出目录", "score": 10, "max_score": 10, "passed": True, "reason": "board_submission 目录存在"})
    else:
        score_details.append({"item": "检查目标输出目录", "score": 0, "max_score": 10, "passed": False, "reason": "board_submission 目录缺失"})
        
    # Check 2: JSON 文件存在性及格式校验 (10 分)
    json_path = os.path.join(board_dir, "verified_hours.json")
    json_data = None
    if os.path.isfile(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            total_score += 10
            score_details.append({"item": "检查 verified_hours.json 格式", "score": 10, "max_score": 10, "passed": True, "reason": "JSON格式完全合法"})
        except Exception as e:
            score_details.append({"item": "检查 verified_hours.json 格式", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {e}"})
    else:
        score_details.append({"item": "检查 verified_hours.json 格式", "score": 0, "max_score": 10, "passed": False, "reason": "verified_hours.json 文件缺失"})
        
    # Check 3: 严格校验人员授权及幻觉，剔除未授权名单 (20 分)
    if json_data is not None and isinstance(json_data, dict):
        approved_staff = ["Dr. Adams", "Nurse Sarah", "Dr. Chen", "Paramedic Joe"]
        unapproved_found = [k for k in json_data.keys() if k not in approved_staff]
        if len(unapproved_found) == 0:
            total_score += 20
            score_details.append({"item": "检查是否剔除未授权人员", "score": 20, "max_score": 20, "passed": True, "reason": "未发现未经授权的杂乱人员数据"})
        else:
            score_details.append({"item": "检查是否剔除未授权人员", "score": 0, "max_score": 20, "passed": False, "reason": f"幻觉或过滤失败，包含未授权人员: {unapproved_found}"})
    else:
        score_details.append({"item": "检查是否剔除未授权人员", "score": 0, "max_score": 20, "passed": False, "reason": "JSON 数据结构无效，无法执行交叉验证"})
        
    # Check 4: 精准校验已知多源数据的合并计算 (30 分)
    # Dr. Adams 仅存在于 CSV (12); Nurse Sarah 存在于 CSV(8) + Email(5) = 13; Dr. Chen 仅存在于 Email (10)
    # (Paramedic Joe 的数据在待 OCR 的 PDF 中，属于动态获取范围，此处做宽容处理，仅校验已知确定数值)
    if json_data is not None and isinstance(json_data, dict):
        math_score = 0
        reasons = []
        
        adams_val = extract_number(json_data.get("Dr. Adams"))
        if adams_val == 12:
            math_score += 10
            reasons.append("Dr. Adams(12)")
            
        sarah_val = extract_number(json_data.get("Nurse Sarah"))
        if sarah_val == 13:
            math_score += 10
            reasons.append("Nurse Sarah(13, 已合并)")
            
        chen_val = extract_number(json_data.get("Dr. Chen"))
        if chen_val == 10:
            math_score += 10
            reasons.append("Dr. Chen(10)")
            
        total_score += math_score
        score_details.append({"item": "检查确定的工时跨文件合并计算", "score": math_score, "max_score": 30, "passed": math_score == 30, "reason": f"成功计算项: {reasons}"})
    else:
        score_details.append({"item": "检查确定的工时跨文件合并计算", "score": 0, "max_score": 30, "passed": False, "reason": "缺失有效的 JSON 字典以验证"})
        
    # Check 5: EMR 导出的联系方式文件是否存在 (10 分)
    contact_path = os.path.join(board_dir, "luthier_contact.txt")
    contact_text = ""
    if os.path.isfile(contact_path):
        with open(contact_path, "r", encoding="utf-8") as f:
            contact_text = f.read().strip()
        if contact_text:
            total_score += 10
            score_details.append({"item": "检查联系人文档生成", "score": 10, "max_score": 10, "passed": True, "reason": "luthier_contact.txt 存在且包含内容"})
        else:
            score_details.append({"item": "检查联系人文档生成", "score": 0, "max_score": 10, "passed": False, "reason": "luthier_contact.txt 是空文件"})
    else:
        score_details.append({"item": "检查联系人文档生成", "score": 0, "max_score": 10, "passed": False, "reason": "luthier_contact.txt 文件缺失"})
        
    # Check 6: 利用 LLM 语义判断 EMR 的动态手机号码返回是否符合现实 (20 分)
    if contact_text:
        prompt = (
            "Determine if the content contains a validly retrieved phone number for a patient. "
            "It must contain a realistic phone number sequence (digits, optional dashes/parentheses/+). "
            "If it contains a phone number or states one, return YES. If it implies failure, hallucination, or is unrelated text, return NO."
        )
        is_valid = llm_judge_content(prompt, contact_text)
        if is_valid:
            total_score += 20
            score_details.append({"item": "利用大模型检查联系号码的合法性", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定内容包含有效提取的电话号码"})
        else:
            score_details.append({"item": "利用大模型检查联系号码的合法性", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定内容不包含电话号码，疑似未提取成功或严重幻觉"})
    else:
        score_details.append({"item": "利用大模型检查联系号码的合法性", "score": 0, "max_score": 20, "passed": False, "reason": "因文件为空，跳过大模型语义验证"})

    # 输出标准化的得分结构
    output_data = {
        "total_score": total_score,
        "details": score_details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    verify()
