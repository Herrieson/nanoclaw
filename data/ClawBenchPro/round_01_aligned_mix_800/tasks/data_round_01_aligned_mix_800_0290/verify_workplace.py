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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "reports", "commission_audit.json")
    
    score = 0
    details = []
    
    # 1. 检查物理目录及文件格式
    if not os.path.exists(report_path):
        details.append({"item": "检查结果文件存在性", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 reports/commission_audit.json"})
        return {"total_score": 0, "details": details}
        
    details.append({"item": "检查结果文件存在性", "score": 10, "max_score": 10, "passed": True, "reason": "文件已按要求生成"})
    
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        details.append({"item": "检查 JSON Schema", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 文件解析成功"})
    except Exception as e:
        details.append({"item": "检查 JSON Schema", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        return {"total_score": 20, "details": details}

    # 辅助搜索函数
    def find_staff(name_kw):
        stack = [data]
        while stack:
            curr = stack.pop()
            if isinstance(curr, dict):
                if name_kw.lower() in str(curr.get('name', '')).lower():
                    return curr
                stack.extend(curr.values())
            elif isinstance(curr, list):
                stack.extend(curr)
        return None

    # 2. 数据隔离与清洗 (排除 retail/admin)
    luka = find_staff("Luka")
    sarah = find_staff("Sarah")
    if not luka and not sarah:
        details.append({"item": "多源数据清洗：排除非相关人员", "score": 20, "max_score": 20, "passed": True, "reason": "成功根据 role 过滤了 Retail 和 Admin 员工"})
        score += 20
    else:
        details.append({"item": "多源数据清洗：排除非相关人员", "score": 0, "max_score": 20, "passed": False, "reason": "报告内错误包含了应被忽略的员工（Luka Chen 或 Admin Sarah）"})

    # 3. 复杂计算逻辑校验
    # Elena: 10000 * 5% + 20000 * 2.5% = 1000
    elena = find_staff("Elena Akana")
    elena_score = 0
    if elena:
        if elena.get('total_volume') == 30000: elena_score += 10
        if elena.get('total_commission') == 1000: elena_score += 10
    if elena_score == 20:
        details.append({"item": "Elena 数据精准度", "score": 20, "max_score": 20, "passed": True, "reason": "多单据叠加及不同环保调控比例的提成计算完全正确"})
    else:
        details.append({"item": "Elena 数据精准度", "score": elena_score, "max_score": 20, "passed": False, "reason": f"计算存在偏差，当前对象数据为: {elena}"})
    score += elena_score

    # Kai: 15000 * 5% = 750 (忽略异常单据 A-99 的提成)
    kai = find_staff("Kai Mana")
    kai_score = 0
    if kai:
        if kai.get('total_volume') in [15000, 20000]: kai_score += 5 # 容忍将无效单算作 volume 的理解偏差，但扣取细节分
        if kai.get('total_volume') == 15000: kai_score += 2
        if kai.get('total_commission') == 750: kai_score += 8
    if kai_score == 15:
        details.append({"item": "Kai 数据精准度", "score": 15, "max_score": 15, "passed": True, "reason": "正确剔除异常单据的提成干扰"})
    else:
        details.append({"item": "Kai 数据精准度", "score": kai_score, "max_score": 15, "passed": False, "reason": f"计算存在偏差，当前对象数据为: {kai}"})
    score += kai_score

    # Mele: 10000 * 2.5% = 250
    mele = find_staff("Mele Hina")
    mele_score = 0
    if mele:
        if mele.get('total_volume') == 10000: mele_score += 5
        if mele.get('total_commission') == 250: mele_score += 10
    if mele_score == 15:
        details.append({"item": "Mele 数据精准度", "score": 15, "max_score": 15, "passed": True, "reason": "单笔调控类别计算完全正确"})
    else:
        details.append({"item": "Mele 数据精准度", "score": mele_score, "max_score": 15, "passed": False, "reason": f"计算存在偏差，当前对象数据为: {mele}"})
    score += mele_score

    # 4. 异常处理捕获
    raw_str = json.dumps(data)
    has_anomaly = "A-99" in raw_str or "D104" in raw_str
    if has_anomaly and ("anomal" in raw_str.lower() or "anomalies" in raw_str.lower()):
        details.append({"item": "缺失资产的异常捕获", "score": 10, "max_score": 10, "passed": True, "reason": "成功在专门的 anomalies 字段或列表中指出了 D104 / A-99 异常情况"})
        score += 10
    else:
        details.append({"item": "缺失资产的异常捕获", "score": 0, "max_score": 10, "passed": False, "reason": "未在报告中明确列出单据中的异常资产(A-99 / D104)"})

    total_score = 20 + score

    # 最终输出
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    verify()
