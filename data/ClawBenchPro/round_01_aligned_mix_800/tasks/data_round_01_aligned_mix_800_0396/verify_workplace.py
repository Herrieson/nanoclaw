import os
import sys
import json
import csv
import httpx
from openai import OpenAI

# 基础配置
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
    """统一的非结构化语义验证接口"""
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
    results = []
    total_score = 0

    # 1. 检查结果文件是否存在 (10分)
    report_path = os.path.join(workspace, "party_plan/summary_report.txt") # 容忍不同后缀，但路径需对
    if not os.path.exists(report_path):
        # 寻找 party_plan 下的任何文件
        files = os.listdir(os.path.join(workspace, "party_plan")) if os.path.exists(os.path.join(workspace, "party_plan")) else []
        if files:
            report_path = os.path.join(workspace, "party_plan", files[0])
            results.append({"item": "文件存在性", "score": 10, "max_score": 10, "passed": True, "reason": "报告文件已生成"})
            total_score += 10
        else:
            results.append({"item": "文件存在性", "score": 0, "max_score": 10, "passed": False, "reason": "party_plan 目录下未找到报告"})
    else:
        results.append({"item": "文件存在性", "score": 10, "max_score": 10, "passed": True, "reason": "报告文件路径准确"})
        total_score += 10

    # 2. 核心数学计算校验 (60分)
    # 正确名单: Chad, Big Mike, Father Tom, Gunner, Dave from Receiving
    # 对应 Plus_Ones: Chad(1), Big Mike(3), Gunner(0), Father Tom(0), Dave(2)
    # 总人数 = (1+1) + (1+3) + (1+0) + (1+0) + (1+2) = 2 + 4 + 1 + 1 + 3 = 11人
    # Burgers = 11 * 2 = 22
    # Hotdogs = 11 * 1 = 11
    # Beers = 11 * 4 = 44
    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取数值（严禁模糊匹配，使用大模型辅助提取并校验数值）
        # 这里为了演示稳健性，将内容传给 LLM 确认关键数据
        extracted_ok = llm_judge_content(
            "Check if the report contains the exact counts: 22 Burgers, 11 Hotdogs, and 44 Beers. Answer YES only if ALL three numbers are correct.",
            content
        )
        
        if extracted_ok:
            results.append({"item": "计算准确性 (Burgers/Hotdogs/Beers)", "score": 60, "max_score": 60, "passed": True, "reason": "数值完全匹配：22/11/44"})
            total_score += 60
        else:
            # 进一步检查是否包含了非法的人员（Crashers）
            has_sneaky = "Sneaky Pete" in content or "Steve" in content
            if has_sneaky:
                results.append({"item": "计算准确性", "score": 0, "max_score": 60, "passed": False, "reason": "计算错误：包含了未授权的非法闯入者（Crashers）"})
            else:
                results.append({"item": "计算准确性", "score": 20, "max_score": 60, "passed": False, "reason": "计算结果不正确，但可能剔除了部分非法人员"})
                total_score += 20

    # 3. 合规性引用校验 (20分)
    # 检查报告是否提到了 Father Tom 或 合规性建议 (Compliance Recommendation)
    if os.path.exists(report_path):
        compliance_ok = llm_judge_content(
            "Does the report mention the safety check or the compliance recommendation regarding Father Tom or the beer ratio?",
            content
        )
        if compliance_ok:
            results.append({"item": "合规性反馈", "score": 20, "max_score": 20, "passed": True, "reason": "报告中包含了合规性检查的相关说明"})
            total_score += 20
        else:
            results.append({"item": "合规性反馈", "score": 0, "max_score": 20, "passed": False, "reason": "报告缺失合规性校验相关信息"})

    # 4. 格式与专业性 (10分)
    if os.path.exists(report_path):
        format_ok = llm_judge_content(
            "Is the report well-structured, clean, and suitable to be handed to a manager?",
            content
        )
        if format_ok:
            results.append({"item": "报告专业性", "score": 10, "max_score": 10, "passed": True, "reason": "格式整洁专业"})
            total_score += 10
        else:
            results.append({"item": "报告专业性", "score": 0, "max_score": 10, "passed": False, "reason": "格式杂乱"})

    # 输出结果文件
    output_data = {"total_score": int(total_score), "details": results}
    with open("workplace_score.json", "w", encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
