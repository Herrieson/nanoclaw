import os
import sys
import json
import httpx
import re
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

def verify_workplace(workspace):
    score_details = []
    total_score = 0
    
    target_dir = os.path.join(workspace, "organized_life")
    target_file = os.path.join(target_dir, "baby_schedule.txt")
    
    # 1. 目录存在性 (10 points)
    if os.path.isdir(target_dir):
        score_details.append({"item": "检查目标目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "organized_life 目录已创建"})
        total_score += 10
    else:
        score_details.append({"item": "检查目标目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "organized_life 目录未找到"})
        
    # 2. 文件存在性 (10 points)
    file_content = ""
    if os.path.isfile(target_file):
        score_details.append({"item": "检查目标文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "baby_schedule.txt 已创建"})
        total_score += 10
        with open(target_file, "r", encoding="utf-8") as f:
            file_content = f.read()
    else:
        score_details.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "baby_schedule.txt 未找到"})

    if file_content:
        content_lower = file_content.lower()
        
        # 3. 必须包含的 11月小孩日程 (20 points)
        pediatrician_in = "pediatrician" in content_lower
        daycare_in = "daycare" in content_lower
        
        inclusion_score = (10 if pediatrician_in else 0) + (10 if daycare_in else 0)
        total_score += inclusion_score
        score_details.append({
            "item": "验证是否提取了 11 月的 Baby 日程", 
            "score": inclusion_score, 
            "max_score": 20, 
            "passed": inclusion_score == 20, 
            "reason": f"Pediatrician: {pediatrician_in}, Daycare: {daycare_in}"
        })
        
        # 4. 严禁包含的干扰项（其他月份、学习、维修） (30 points)
        forbidden_keywords = ["flu shot", "math test", "ipad", "soldering", "history", "18-month"]
        found_forbidden = [kw for kw in forbidden_keywords if kw in content_lower]
        
        if len(found_forbidden) == 0:
            score_details.append({"item": "严查幻觉与噪音数据提取", "score": 30, "max_score": 30, "passed": True, "reason": "成功排除了所有非11月及非小孩的干扰项"})
            total_score += 30
        else:
            penalty = len(found_forbidden) * 10
            actual_score = max(0, 30 - penalty)
            total_score += actual_score
            score_details.append({"item": "严查幻觉与噪音数据提取", "score": actual_score, "max_score": 30, "passed": False, "reason": f"混入了错误数据: {', '.join(found_forbidden)}"})
            
        # 5. LLM 语义检查: 末尾是否附带了维修副业的净利润数值 (30 points)
        prompt_text = (
            "Examine the text carefully. At or near the bottom, is there a clear statement declaring a "
            "financial amount specifically for 'net profit' (or total profit/earnings) derived from tech repairs? "
            "It must clearly state a dollar amount (e.g., $150.00) and represent the final subtracted profit, not just a list of items."
        )
        has_net_profit = llm_judge_content(prompt_text, file_content)
        
        # 兜底：如果 LLM 失败，使用正则表达式检查是否有美元符号及数值
        if not has_net_profit:
            has_net_profit = bool(re.search(r'\$\d+(\.\d{2})?', file_content)) and "profit" in content_lower
            
        if has_net_profit:
            score_details.append({"item": "检查是否计算并附加了总净利润金额", "score": 30, "max_score": 30, "passed": True, "reason": "文本中包含明确的净利润金额声明"})
            total_score += 30
        else:
            score_details.append({"item": "检查是否计算并附加了总净利润金额", "score": 0, "max_score": 30, "passed": False, "reason": "未找到明确的总净利润数值或声明"})
            
    else:
        # File missing or empty
        score_details.append({"item": "验证是否提取了 11 月的 Baby 日程", "score": 0, "max_score": 20, "passed": False, "reason": "文件为空或不存在"})
        score_details.append({"item": "严查幻觉与噪音数据提取", "score": 0, "max_score": 30, "passed": False, "reason": "文件为空或不存在"})
        score_details.append({"item": "检查是否计算并附加了总净利润金额", "score": 0, "max_score": 30, "passed": False, "reason": "文件为空或不存在"})

    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    ws = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(ws)
