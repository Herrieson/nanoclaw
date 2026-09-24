import os
import sys
import json
import re
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-3.5-turbo")

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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results_dir = os.path.join(workspace, "audit_results")
    
    score_details = []
    total_score = 0

    # 1. 检查目录和报告文件是否存在 (10分)
    has_dir = os.path.isdir(results_dir)
    report_content = ""
    if has_dir:
        files = os.listdir(results_dir)
        if files:
            # 假设有一个包含总结的报告文件
            report_file = os.path.join(results_dir, files[0])
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    report_content = f.read()
                score_details.append({"item": "检查结果目录与报告文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": f"目录存在且找到文件 {files[0]}"})
                total_score += 10
            except Exception as e:
                score_details.append({"item": "检查结果目录与报告文件是否存在", "score": 5, "max_score": 10, "passed": False, "reason": "找到文件但无法读取"})
                total_score += 5
        else:
            score_details.append({"item": "检查结果目录与报告文件是否存在", "score": 5, "max_score": 10, "passed": False, "reason": "目录存在但为空"})
            total_score += 5
    else:
        score_details.append({"item": "检查结果目录与报告文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "audit_results 目录不存在"})
        
    if not report_content:
        # 没有内容直接结束，后续计0分
        score_details.extend([
            {"item": "精确提取并验证正确合规索赔总金额", "score": 0, "max_score": 30, "passed": False, "reason": "无报告文件"},
            {"item": "验证异常索赔记录清单的完整性", "score": 0, "max_score": 30, "passed": False, "reason": "无报告文件"},
            {"item": "验证不存在误报(False Positives)", "score": 0, "max_score": 10, "passed": False, "reason": "无报告文件"},
            {"item": "大模型语义校验报告结构与语气", "score": 0, "max_score": 20, "passed": False, "reason": "无报告文件"}
        ])
    else:
        # 2. 精确提取并验证最终合规索赔金额 (30分)
        # 正确的总金额应为 32600
        if re.search(r'\b32600\b', report_content):
            score_details.append({"item": "精确提取并验证正确合规索赔总金额", "score": 30, "max_score": 30, "passed": True, "reason": "成功找到正确的合规金额 32600"})
            total_score += 30
        else:
            score_details.append({"item": "精确提取并验证正确合规索赔总金额", "score": 0, "max_score": 30, "passed": False, "reason": "未找到正确的合规金额 32600，计算错误或格式错误"})

        # 3. 验证异常索赔记录清单 (包含且仅包含指定项) (30分)
        expected_exceptions = {"C-102", "C-103", "C-202", "C-204"}
        found_exceptions = set()
        for exc in expected_exceptions:
            if exc in report_content:
                found_exceptions.add(exc)
        
        exception_score = int(30 * (len(found_exceptions) / len(expected_exceptions)))
        passed_exceptions = exception_score == 30
        score_details.append({"item": "验证异常索赔记录清单的完整性", "score": exception_score, "max_score": 30, "passed": passed_exceptions, "reason": f"找到了 {len(found_exceptions)}/4 个应有的异常记录"})
        total_score += exception_score

        # 4. 严查幻觉/误报 (10分)
        # 合规的记录不应该出现在“异常”或单纯的负面词汇上下文中，此处采取强硬规则：
        # 如果它们在文本里出现，极有可能被错误归类到了异常单中（除非明确区分，但简单文本里大概率是弄错了）
        valid_claims = {"C-101", "C-104", "C-201", "C-203"}
        false_positives = [vc for vc in valid_claims if vc in report_content]
        
        # 为了防误杀，采用大模型确认是否将合规单列为异常单
        if false_positives:
            fp_prompt = "请检查以下报告，判断作者是否把 C-101, C-104, C-201, C-203 中的任意一个列为了'异常'或'超限'或'非法'记录？如果是，回答 YES。如果仅仅是作为正常记录列出，回答 NO。"
            has_fp = llm_judge_content(fp_prompt, report_content)
            if has_fp:
                score_details.append({"item": "验证不存在误报(False Positives)", "score": 0, "max_score": 10, "passed": False, "reason": "报告中错误地将合法的索赔记录列为异常，严厉扣分"})
            else:
                score_details.append({"item": "验证不存在误报(False Positives)", "score": 10, "max_score": 10, "passed": True, "reason": "虽提及合法单号，但未将其错误归类为异常"})
                total_score += 10
        else:
            score_details.append({"item": "验证不存在误报(False Positives)", "score": 10, "max_score": 10, "passed": True, "reason": "报告中未将合法的索赔单号列为异常"})
            total_score += 10

        # 5. LLM 检查报告语义完整度与语气 (20分)
        semantic_prompt = (
            "Please read the following insurance claims audit report. "
            "Does the report explicitly state it is summarizing valid claims, clearly separate the invalid/over-limit claims, "
            "and maintain a professional, clear structure? Answer YES if it does, NO if it is confusing, lacks structure, or feels unprofessional."
        )
        if llm_judge_content(semantic_prompt, report_content):
            score_details.append({"item": "大模型语义校验报告结构与语气", "score": 20, "max_score": 20, "passed": True, "reason": "报告语义清晰，结构和语气符合要求"})
            total_score += 20
        else:
            score_details.append({"item": "大模型语义校验报告结构与语气", "score": 0, "max_score": 20, "passed": False, "reason": "报告缺乏清晰的结构或未明确区分正常/异常项"})

    # 输出 JSON
    output_data = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
