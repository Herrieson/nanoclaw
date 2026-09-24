#!/usr/bin/env python3

import os
import sys
import json
import httpx
import re
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 强制关闭 SSL 验证并初始化客户端
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """使用大模型进行非结构化语义验证"""
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

def check_amount(content):
    """混合验证：优先使用正则匹配确保数值确定性，失败时借助大模型语义理解"""
    # 严格匹配 57.5 或 57.50
    if re.search(r'57\.50?', content):
        return True
    return llm_judge_content("Does the document explicitly state that the total amount owed is 57.50 (or 57 dollars and 50 cents)?", content)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_dir = os.path.join(workspace, "finances_and_birds")
    
    details = []
    total_score = 0
    
    # 验证项 1: 检查目录结构 (10分)
    dir_exists = os.path.isdir(target_dir)
    if dir_exists:
        details.append({"item": "检查目标目录 finances_and_birds 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
        total_score += 10
    else:
        details.append({"item": "检查目标目录 finances_and_birds 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录不存在"})
        
    # 验证项 2: 检查文件是否生成且可读 (10分)
    file_content = ""
    file_exists = False
    if dir_exists:
        try:
            files = [f for f in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, f))]
            if files:
                file_exists = True
                # 拼接所有文件内容以防Agent拆分文件
                for f in files:
                    with open(os.path.join(target_dir, f), "r", encoding="utf-8") as file:
                        file_content += file.read() + "\n"
        except Exception:
            pass

    if file_exists and file_content.strip():
        details.append({"item": "检查目标目录中是否存在并成功读取总结文件", "score": 10, "max_score": 10, "passed": True, "reason": "成功读取总结文件内容"})
        total_score += 10
    else:
        details.append({"item": "检查目标目录中是否存在并成功读取总结文件", "score": 0, "max_score": 10, "passed": False, "reason": "未找到文件或文件为空"})

    # 若未能读取到内容，后续语义验证直接判负
    if not file_content.strip():
        details.extend([
            {"item": "检查总欠款金额是否正确计算为 57.50", "score": 0, "max_score": 20, "passed": False, "reason": "文件为空无法验证"},
            {"item": "检查是否准确列出所有未付款人(Sarah, John, Alice, Dave)", "score": 0, "max_score": 20, "passed": False, "reason": "文件为空无法验证"},
            {"item": "检查是否排除了已付款人(Tom, Mark)", "score": 0, "max_score": 10, "passed": False, "reason": "文件为空无法验证"},
            {"item": "检查是否准确列出按叫声识别的鸟类", "score": 0, "max_score": 20, "passed": False, "reason": "文件为空无法验证"},
            {"item": "检查是否排除了未按叫声识别的鸟类", "score": 0, "max_score": 10, "passed": False, "reason": "文件为空无法验证"},
        ])
    else:
        # 验证项 3: 检查计算结果 (20分)
        if check_amount(file_content):
            details.append({"item": "检查总欠款金额是否正确计算为 57.50", "score": 20, "max_score": 20, "passed": True, "reason": "包含正确的汇总金额 57.50"})
            total_score += 20
        else:
            details.append({"item": "检查总欠款金额是否正确计算为 57.50", "score": 0, "max_score": 20, "passed": False, "reason": "金额计算错误或未在文中体现"})
            
        # 验证项 4: 检查欠款人员名单是否完整 (20分)
        unpaid_prompt = "Does the document explicitly list Sarah, John, Alice, and Dave as the people who owe money (unpaid)? Respond 'YES' only if all four are listed as unpaid."
        if llm_judge_content(unpaid_prompt, file_content):
            details.append({"item": "检查是否准确列出所有未付款人(Sarah, John, Alice, Dave)", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定：准确列出了所有未付款人"})
            total_score += 20
        else:
            details.append({"item": "检查是否准确列出所有未付款人(Sarah, John, Alice, Dave)", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定：未正确列出所有未付款人"})

        # 验证项 5: 严查幻觉/假阳性 - 是否混入了已付款的人 (10分)
        exclude_paid_prompt = "Does the document correctly EXCLUDE Tom and Mark from the list of people who owe money? (i.e., they are either not mentioned, or explicitly mentioned as having paid). Answer 'YES' if they are correctly excluded or marked as paid. Answer 'NO' if they are mistakenly listed as owing money."
        if llm_judge_content(exclude_paid_prompt, file_content):
            details.append({"item": "检查是否排除了已付款人(Tom, Mark)", "score": 10, "max_score": 10, "passed": True, "reason": "大模型判定：未将已付款人错误列入欠款名单"})
            total_score += 10
        else:
            details.append({"item": "检查是否排除了已付款人(Tom, Mark)", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定：错误地将已付款人列入欠款名单"})

        # 验证项 6: 检查通过叫声识别的鸟类名单是否完整 (20分)
        birds_prompt = "Does the document explicitly list Black-capped Chickadee, Blue Jay, Eastern Towhee, and Northern Cardinal as birds identified by their calls? Answer 'YES' only if all four are included."
        if llm_judge_content(birds_prompt, file_content):
            details.append({"item": "检查是否准确列出按叫声识别的鸟类", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定：准确列出了所有指定的鸟类"})
            total_score += 20
        else:
            details.append({"item": "检查是否准确列出按叫声识别的鸟类", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定：遗漏了指定的按叫声识别的鸟类"})

        # 验证项 7: 严查幻觉/假阳性 - 是否混入了非叫声识别的鸟类 (10分)
        exclude_birds_prompt = "Does the document correctly EXCLUDE Robin and Woodpecker from the list of birds identified by their calls? (They were either just seen, or drumming, not vocalizing). Answer 'YES' if Robin and Woodpecker are correctly excluded from the vocal call list. Answer 'NO' if they are mistakenly included."
        if llm_judge_content(exclude_birds_prompt, file_content):
            details.append({"item": "检查是否排除了未按叫声识别的鸟类(Robin, Woodpecker)", "score": 10, "max_score": 10, "passed": True, "reason": "大模型判定：正确排除了非叫声识别的鸟类"})
            total_score += 10
        else:
            details.append({"item": "检查是否排除了未按叫声识别的鸟类(Robin, Woodpecker)", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定：幻觉或错误地将非叫声识别鸟类加入列表"})

    # 输出统一规范的打分结果
    score_dict = {
        "total_score": total_score,
        "details": details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(score_dict, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
