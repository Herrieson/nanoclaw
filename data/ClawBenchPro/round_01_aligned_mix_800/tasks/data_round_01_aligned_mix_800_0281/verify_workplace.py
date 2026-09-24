import os
import sys
import json
import httpx
import re
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
    """利用大模型进行非结构化语义验证"""
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

def verify_workplace(workspace):
    score_details = []
    total_score = 0

    reports_dir = os.path.join(workspace, "reports")
    
    # 1. 检查目录创建 (10分)
    if os.path.isdir(reports_dir):
        score_details.append({"item": "检查 reports 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查 reports 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 reports 目录"})
        # 目录不存在，后续检查大概率失败，但为了鲁棒性，还是尝试读取当前目录
        reports_dir = workspace

    # 读取所有报告文件内容
    report_files = [f for f in os.listdir(reports_dir) if os.path.isfile(os.path.join(reports_dir, f)) and f.endswith(('.txt', '.md', '.csv', '.json'))]
    all_reports_text = ""
    for rf in report_files:
        try:
            with open(os.path.join(reports_dir, rf), "r", encoding="utf-8") as file:
                all_reports_text += file.read() + "\n"
        except:
            pass

    if not all_reports_text:
        score_details.append({"item": "检查是否生成了报告文件", "score": 0, "max_score": 90, "passed": False, "reason": "未在 reports 目录找到任何合法文本报告"})
    else:
        # 2. 差异报告核心数值检查：Total Overcharge = 14.00 (30分)
        # CleanCorp WAX_002 (10) + CHEM_001 (1) + SOAP_005 (3) = 14.00
        if re.search(r'\b14\.00\b|\b14\b', all_reports_text):
            score_details.append({"item": "精确提取总超额收费数值(14.00)", "score": 30, "max_score": 30, "passed": True, "reason": "成功计算并输出了正确的超收总额 $14.00"})
            total_score += 30
        else:
            score_details.append({"item": "精确提取总超额收费数值(14.00)", "score": 0, "max_score": 30, "passed": False, "reason": "未在报告中找到计算正确的总超收额(14.00)，可能是漏算了 OCR 数据或普通 CSV 数据"})

        # 3. 库存健康报告：低库存对象识别 (30分)
        # 小于 5 的物品: WAX_002(2), SOAP_005(1), BRUSH_004(3).
        # 不应包含: CHEM_001(12), MOP_003(5) (5不满足小于5的条件)
        has_wax = "WAX_002" in all_reports_text
        has_soap = "SOAP_005" in all_reports_text
        has_brush = "BRUSH_004" in all_reports_text
        has_chem = "CHEM_001" in all_reports_text
        has_mop = "MOP_003" in all_reports_text
        
        stock_score = 0
        if has_wax and has_soap and has_brush:
            if not has_chem and not has_mop:
                stock_score = 30
                score_details.append({"item": "低库存(不足5件)物品识别准确性", "score": 30, "max_score": 30, "passed": True, "reason": "精准筛选出 WAX_002, SOAP_005, BRUSH_004 且排除了临界值 MOP_003"})
            else:
                stock_score = 15
                score_details.append({"item": "低库存(不足5件)物品识别准确性", "score": 15, "max_score": 30, "passed": False, "reason": "找出了所需低库存物品，但错误地包含了 CHEM_001 或 MOP_003（数量 >= 5）"})
        else:
            score_details.append({"item": "低库存(不足5件)物品识别准确性", "score": 0, "max_score": 30, "passed": False, "reason": "未能找出所有低库存物品（WAX_002, SOAP_005, BRUSH_004）"})
        total_score += stock_score

        # 4. 库存健康报告：Operational Days Remaining 的精确数值验证 (20分)
        # WAX_002: 10, SOAP_005: 0.8, BRUSH_004: 60
        days_correct = all(x in all_reports_text for x in ["10", "0.8", "60"])
        if days_correct:
            score_details.append({"item": "验证 Operational Days 计算结果", "score": 20, "max_score": 20, "passed": True, "reason": "正确包含工具计算出的运营天数：10, 0.8, 60"})
            total_score += 20
        else:
            score_details.append({"item": "验证 Operational Days 计算结果", "score": 0, "max_score": 20, "passed": False, "reason": "未能准确提取/调用优化器得出正确的 operational days（10, 0.8, 60）"})

        # 5. 利用大模型进行语义检查 (10分)
        # 确保 Agent 在报告中恰当地说明了超收原因并且指出了这是 CleanCorp 导致的。
        prompt = "Does the report clearly explicitly state that 'CleanCorp' is the supplier responsible for the overcharges and discrepancies?"
        if llm_judge_content(prompt, all_reports_text[:3000]):
            score_details.append({"item": "利用大模型检查报告语义与归责", "score": 10, "max_score": 10, "passed": True, "reason": "报告中明确且清晰地将超收问题归咎于 CleanCorp"})
            total_score += 10
        else:
            score_details.append({"item": "利用大模型检查报告语义与归责", "score": 0, "max_score": 10, "passed": False, "reason": "报告中未能明确交代是 CleanCorp 造成了计费差异"})

    # 输出最终结果
    result = {
        "total_score": total_score,
        "details": score_details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(workspace)
