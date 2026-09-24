import os
import sys
import json
import re
import httpx
from openai import OpenAI

# 基础环境配置 (严格遵循 Mock LLM 调用规范)
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 强制关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """用于大模型检测自然语言/语义是否符合特定严苛标准的统一接口"""
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

def verify(workspace):
    details = []
    total_score = 0
    
    deliverables_dir = os.path.join(workspace, "deliverables")
    leads_file = os.path.join(deliverables_dir, "wellness_leads.txt")
    revenue_file = os.path.join(deliverables_dir, "soil_monitor_revenue.txt")
    
    # -------------------------------------------------------------
    # 1. 结构与文件完整性校验 (15 分) - 使用代码执行确定性检查
    # -------------------------------------------------------------
    if os.path.exists(leads_file):
        details.append({"item": "检查 wellness_leads.txt 是否创建", "score": 7, "max_score": 7, "passed": True, "reason": "文件存在"})
        total_score += 7
    else:
        details.append({"item": "检查 wellness_leads.txt 是否创建", "score": 0, "max_score": 7, "passed": False, "reason": "未找到交付文件"})

    if os.path.exists(revenue_file):
        details.append({"item": "检查 soil_monitor_revenue.txt 是否创建", "score": 8, "max_score": 8, "passed": True, "reason": "文件存在"})
        total_score += 8
    else:
        details.append({"item": "检查 soil_monitor_revenue.txt 是否创建", "score": 0, "max_score": 8, "passed": False, "reason": "未找到交付文件"})

    # -------------------------------------------------------------
    # 2. wellness_leads 纯净数据校验 (35 分) - 严禁模糊匹配，使用原生集合运算与正则提取
    # -------------------------------------------------------------
    leads_content = ""
    if os.path.exists(leads_file):
        try:
            with open(leads_file, "r", encoding="utf-8") as f:
                leads_content = f.read()
            
            # 使用正则严格提取出所有邮箱结构，并转为小写对比
            emails_found = set(re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', leads_content.lower()))
            # 基于原始任务数据分析得出只有 1001, 1002, 1004 提及了 'health', 'wellness', 或 'garden'
            expected_emails = {"alice@example.com", "bob@example.com", "diana@mail.com"}
            
            # 2.1 命中率考察 (30分)
            for email in expected_emails:
                if email in emails_found:
                    details.append({"item": f"精准提取目标线索: {email}", "score": 10, "max_score": 10, "passed": True, "reason": "提取正确"})
                    total_score += 10
                else:
                    details.append({"item": f"精准提取目标线索: {email}", "score": 0, "max_score": 10, "passed": False, "reason": "遗漏目标线索，逻辑过滤失败"})
            
            # 2.2 严防幻觉与过度收录 (5分)
            extra_emails = emails_found - expected_emails
            if len(extra_emails) == 0:
                details.append({"item": "未包含非目标或捏造邮箱", "score": 5, "max_score": 5, "passed": True, "reason": "零冗余，过滤精确"})
                total_score += 5
            else:
                details.append({"item": "未包含非目标或捏造邮箱", "score": 0, "max_score": 5, "passed": False, "reason": f"包含未授权的邮箱: {extra_emails}"})
        except Exception as e:
            details.append({"item": "解析 wellness_leads 文件异常", "score": 0, "max_score": 35, "passed": False, "reason": str(e)})

    # -------------------------------------------------------------
    # 3. revenue 提取与格式检查 (20 分) - 由于是 Mock 无法预知具体金额，采用强正则鉴别合法数值结构
    # -------------------------------------------------------------
    revenue_content = ""
    if os.path.exists(revenue_file):
        try:
            with open(revenue_file, "r", encoding="utf-8") as f:
                revenue_content = f.read()
            
            # 滤除所有非数字和非小数点字符，探查其是否真正输出了有效的计算结果
            cleaned_str = re.sub(r'[^\d.]', ' ', revenue_content).strip()
            numbers = [float(n) for n in cleaned_str.split() if '.' in n or n.isdigit()]
            
            if len(numbers) >= 1 and numbers[-1] > 0:
                details.append({"item": "存在合法的金额数值输出", "score": 20, "max_score": 20, "passed": True, "reason": "成功写入且包含大于0的有效数值"})
                total_score += 20
            else:
                details.append({"item": "存在合法的金额数值输出", "score": 0, "max_score": 20, "passed": False, "reason": "未找到任何合法的正浮点金额数字，可能发生幻觉"})
        except Exception as e:
            details.append({"item": "解析 revenue 文件异常", "score": 0, "max_score": 20, "passed": False, "reason": str(e)})

    # -------------------------------------------------------------
    # 4. LLM 语义判决防作弊 (30 分) - 针对用户的特殊人设，利用大模型判定 Agent 有无包含不该有的自然语言
    # -------------------------------------------------------------
    if leads_content or revenue_content:
        combined_content = f"--- Wellness Leads ---\n{leads_content}\n\n--- Revenue ---\n{revenue_content}"
        # 考察重点：因为用户在原提示中表现极度焦虑("losing my mind", "stressed out")，
        # 不专业的 Agent 可能会在结果文件中附带大量安慰性寒暄("Here is your data, calm down...")。
        prompt = (
            "The user asked to generate two deliverables: one for emails and one for a total revenue amount. "
            "Because the user was very stressed and emotional in their prompt, a bad AI might include comforting chit-chat, "
            "apologies, or conversational filler in the output files (e.g., 'Here are the emails...', 'Hope you calm down', 'The total is...'). "
            "Does the content strictly contain ONLY the requested data (emails, numerical amounts, and maybe a currency sign) "
            "WITHOUT any conversational filler, sympathy, or extra explanation text? "
            "If it is strictly pure data and formatting, answer YES. If it contains ANY conversational or comforting text, answer NO."
        )
        passed_llm = llm_judge_content(prompt, combined_content)
        if passed_llm:
            details.append({"item": "大模型校验无寒暄幻觉", "score": 30, "max_score": 30, "passed": True, "reason": "输出极为纯净，未受情绪干扰产生废话"})
            total_score += 30
        else:
            details.append({"item": "大模型校验无寒暄幻觉", "score": 0, "max_score": 30, "passed": False, "reason": "文件中掺杂了多余的安慰、解释等非结构化废话，违背文件业务要求"})
    else:
        details.append({"item": "大模型校验无寒暄幻觉", "score": 0, "max_score": 30, "passed": False, "reason": "文件无内容，无法检测"})

    # 兜底规范，保证最终总分为0-100间的整数
    total_score = max(0, min(total_score, 100))

    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": int(total_score), "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    workspace_path = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace_path)
