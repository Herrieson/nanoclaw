import os
import sys
import json
import re
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

# 初始化客户端，必须关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """用于验证非结构化文本语义的大模型裁判"""
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

def extract_all_numbers(text):
    """提取文本中的所有数字用于精确比对"""
    # 匹配整数和带两位小数的浮点数
    str_nums = re.findall(r'\b\d+(?:\.\d{1,2})?\b', text)
    return [float(n) for n in str_nums]

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_dir = os.path.join(workspace, "ready_for_monday")
    
    total_score = 0
    details = []

    # 1. 结构与目录检查 (10分)
    if os.path.isdir(target_dir):
        total_score += 10
        details.append({"item": "检查目标交付目录", "score": 10, "max_score": 10, "passed": True, "reason": f"目录 {target_dir} 存在"})
    else:
        details.append({"item": "检查目标交付目录", "score": 0, "max_score": 10, "passed": False, "reason": f"目录 {target_dir} 不存在"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 2. 文件结构检查 (10分)
    files = [f for f in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, f))]
    if len(files) >= 2:
        total_score += 10
        details.append({"item": "独立文件分类生成", "score": 10, "max_score": 10, "passed": True, "reason": "成功将财务数据与安全报告分到不同文件中"})
    else:
        score = 5 if len(files) == 1 else 0
        total_score += score
        details.append({"item": "独立文件分类生成", "score": score, "max_score": 10, "passed": False, "reason": f"目标要求安全和财务文件独立，当前仅发现 {len(files)} 个文件"})

    if len(files) == 0:
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 读取所有生成内容进行联合验证
    all_content = ""
    for file_name in files:
        file_path = os.path.join(target_dir, file_name)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                all_content += f"\n--- [{file_name}] ---\n{f.read()}\n"
        except Exception:
            pass

    # 3. 原生代码精准数值校验 - 财务计算与剔除个人消费 (30分)
    # 正确逻辑:
    # Business = 450 + 120 + 15 + 300 = 885.0
    # Art = 35.50 + 85 + 150 = 270.5
    # (Personal = 12 + 42.50 = 54.5 绝对不能算进去)
    extracted_nums = extract_all_numbers(all_content)
    has_business_total = any(abs(n - 885.0) < 0.01 for n in extracted_nums)
    has_art_total = any(abs(n - 270.5) < 0.01 for n in extracted_nums)
    has_personal_contamination = any(abs(n - 54.5) < 0.01 for n in extracted_nums) or any(abs(n - 1210.0) < 0.01 for n in extracted_nums) # 1210 是全加起来的错误总和

    fin_score = 0
    fin_reasons = []
    if has_business_total:
        fin_score += 15
        fin_reasons.append("精准算出建筑材料花费 ($885.0)")
    if has_art_total:
        fin_score += 15
        fin_reasons.append("精准算出艺术废铁花费 ($270.5)")
    if has_personal_contamination:
        fin_score = max(0, fin_score - 15) # 发现包含个人开销或全部混加，扣除逻辑分
        fin_reasons.append("警告：未正确剥离个人消费记录(Snacks/Diapers)，被扣分")

    if fin_score == 30:
        details.append({"item": "原生代码校验财务核心数据", "score": 30, "max_score": 30, "passed": True, "reason": "数据分离严谨，" + "；".join(fin_reasons)})
    else:
        details.append({"item": "原生代码校验财务核心数据", "score": fin_score, "max_score": 30, "passed": False, "reason": "财务计算错误或分类不严，" + "；".join(fin_reasons)})
    total_score += fin_score

    # 4. LLM 语义校验 - 安全隐患精准过滤 (30分)
    safety_prompt = """Analyze the provided documents. Identify the safety report intended for the city safety inspector.
Does the report ONLY include the following two CRITICAL/IMMEDIATE hazards:
1. "Missing guardrails on scaffolding"
2. "Exposed live wire"
AND strictly EXCLUDE the minor issues (such as "missing dust masks" or "hard hats left off")?
Answer 'YES' if it perfectly filters out the minor issues and keeps the critical ones. Answer 'NO' if it misses a critical issue, or includes the minor ones."""
    
    if llm_judge_content(safety_prompt, all_content):
        total_score += 30
        details.append({"item": "LLM语义：安全隐患定级与过滤", "score": 30, "max_score": 30, "passed": True, "reason": "成功提取了脚手架和电线隐患，且未混入 Minor 级别的口罩、安全帽记录"})
    else:
        details.append({"item": "LLM语义：安全隐患定级与过滤", "score": 0, "max_score": 30, "passed": False, "reason": "报告中遗漏了严重安全隐患，或将无关的 Minor 隐患也写给了检查员"})

    # 5. LLM 语义校验 - 职业报告格式 (20分)
    format_prompt = """Analyze the provided documents. Is the safety summary and financial note cleanly formatted, professional, and entirely free of conversational AI filler phrases? 
Examples of AI filler to penalize: "Here is your report", "I have decoded the files", "As an AI", "Sure, I can help".
Answer 'YES' if it is a professional, ready-to-print set of documents. Answer 'NO' if it contains any conversational chat behaviors."""
    
    if llm_judge_content(format_prompt, all_content):
        total_score += 20
        details.append({"item": "LLM语义：交付物去AI化与专业度", "score": 20, "max_score": 20, "passed": True, "reason": "文档格式专业干净，无 AI 客套话废话"})
    else:
        details.append({"item": "LLM语义：交付物去AI化与专业度", "score": 0, "max_score": 20, "passed": False, "reason": "检测到文档内部残留多余的 AI 对话或寒暄用语"})

    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    verify()
