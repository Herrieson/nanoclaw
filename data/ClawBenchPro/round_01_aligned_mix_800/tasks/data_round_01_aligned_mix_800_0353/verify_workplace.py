import os
import sys
import json
import re
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o-mini")

http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """使用 LLM 对非结构化语义进行布尔判断"""
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
    summary_path = os.path.join(workspace, "church_funds", "summary.txt")
    
    details = []
    total_score = 0
    
    # 1. 检查目录结构与目标文件 (10分)
    if os.path.exists(summary_path):
        details.append({
            "item": "检查目标结果文件是否存在", 
            "score": 10, 
            "max_score": 10, 
            "passed": True, 
            "reason": "成功找到 church_funds/summary.txt"
        })
        total_score += 10
        
        with open(summary_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 2. 原生代码：精准数值提取与业务逻辑陷阱校验 (40分)
        # 正确数值: 70.5 或 70.50
        has_correct_amount = bool(re.search(r'70\.50?', content))
        # 错误陷阱: $121 (加入了汽油/个人支出), $75.50 (加入了捐赠)
        has_gas_error = bool(re.search(r'121\.00?|112\.50?', content))
        has_donation_error = bool(re.search(r'75\.50?', content))
        
        if has_correct_amount and not has_gas_error and not has_donation_error:
            details.append({
                "item": "计算 Bake Sale 最终收入金额", 
                "score": 40, 
                "max_score": 40, 
                "passed": True, 
                "reason": "成功计算出 $70.50 且没有错误并入加油站账单或教堂捐赠等干扰项。"
            })
            total_score += 40
        elif has_gas_error:
            details.append({
                "item": "计算 Bake Sale 最终收入金额", 
                "score": 0, 
                "max_score": 40, 
                "passed": False, 
                "reason": "金额错误，由于混入了加油站和个人账单（计算出了 $121.00 类的错误总计），严重违反业务要求。"
            })
        elif has_donation_error:
            details.append({
                "item": "计算 Bake Sale 最终收入金额", 
                "score": 0, 
                "max_score": 40, 
                "passed": False, 
                "reason": "金额错误，错误地将 'Donation' 捐赠款项计入了义卖商品收入（出现了 75.50），违反了牧师定下的归类规则。"
            })
        elif has_correct_amount:
            details.append({
                "item": "计算 Bake Sale 最终收入金额", 
                "score": 20, 
                "max_score": 40, 
                "passed": False, 
                "reason": "虽然在文件中找到了 $70.50，但也包含了其他计算混乱的数值记录，只给一半分。"
            })
            total_score += 20
        else:
            details.append({
                "item": "计算 Bake Sale 最终收入金额", 
                "score": 0, 
                "max_score": 40, 
                "passed": False, 
                "reason": "未能计算或提取出正确的义卖金额 $70.50。"
            })
            
        # 3. 原生代码：检查是否向报告中写入了脏数据 (20分)
        forbidden_words = ['marlboro', 'cigarettes', 'pump', 'diesel', 'scratch-off', 'car wash', '10w30']
        found_forbidden = [w for w in forbidden_words if w in content.lower()]
        if not found_forbidden:
            details.append({
                "item": "严格过滤与剔除不相关单据明细", 
                "score": 20, 
                "max_score": 20, 
                "passed": True, 
                "reason": "输出干净，没有在给牧师的汇总中写入加油站和私人买烟等不雅的账单细目。"
            })
            total_score += 20
        else:
            details.append({
                "item": "严格过滤与剔除不相关单据明细", 
                "score": 0, 
                "max_score": 20, 
                "passed": False, 
                "reason": f"未正确剔除个人开销词汇，报告中发现了脏数据: {', '.join(found_forbidden)}。"
            })

        # 4. 大模型调用：非结构化语境与报告格式检查 (30分)
        prompt_text = (
            "Does the text read like a polite note, report, or summary intended for a Southern church Pastor (e.g., mentioning 'Pastor', 'Church', or showing respect) regarding a Bake Sale? "
            "It should NOT be a raw JSON dump or just a sterile isolated number. It must have some natural language contextual framing."
        )
        is_polite = llm_judge_content(prompt_text, content)
        if is_polite:
            details.append({
                "item": "LLM 语义语境检验与角色代入", 
                "score": 30, 
                "max_score": 30, 
                "passed": True, 
                "reason": "大模型判定内容符合南方教区义卖报告的礼貌标准与语境，并不仅是冰冷的数据输出。"
            })
            total_score += 30
        else:
            details.append({
                "item": "LLM 语义语境检验与角色代入", 
                "score": 0, 
                "max_score": 30, 
                "passed": False, 
                "reason": "大模型判定输出过于生硬（如只给了一个数字或JSON），缺乏对牧师的礼节性前言/说明，未满足角色扮演要求。"
            })

    else:
        details.append({"item": "检查目标结果文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 church_funds/summary.txt 文件。"})
        details.append({"item": "计算 Bake Sale 最终收入金额", "score": 0, "max_score": 40, "passed": False, "reason": "文件缺失，无法验证金额。"})
        details.append({"item": "严格过滤与剔除不相关单据明细", "score": 0, "max_score": 20, "passed": False, "reason": "文件缺失。"})
        details.append({"item": "LLM 语义语境检验与角色代入", "score": 0, "max_score": 30, "passed": False, "reason": "文件缺失。"})

    # 写入最终评测结果
    score_file = os.path.join(workspace, "workplace_score.json")
    with open(score_file, 'w', encoding='utf-8') as f:
        json.dump({
            "total_score": total_score,
            "details": details
        }, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    verify()
