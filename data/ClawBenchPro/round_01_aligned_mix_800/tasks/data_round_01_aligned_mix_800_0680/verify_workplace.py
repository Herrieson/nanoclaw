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
    """LLM 语义检测接口"""
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
    score = 0
    details = []
    
    # 1. 检测目录存在性 (5分)
    dir_path = os.path.join(workspace, "portfolio_summary")
    if os.path.isdir(dir_path):
        details.append({"item": "检查目标目录 portfolio_summary 是否存在", "score": 5, "max_score": 5, "passed": True, "reason": "目录 portfolio_summary 存在"})
        score += 5
    else:
        details.append({"item": "检查目标目录 portfolio_summary 是否存在", "score": 0, "max_score": 5, "passed": False, "reason": "目录 portfolio_summary 不存在"})
        
    # 2. 检测文件存在性 (5分)
    file_path = os.path.join(dir_path, "midnight_revenue.txt")
    file_exists = os.path.isfile(file_path)
    if file_exists:
        details.append({"item": "检查结果文件 midnight_revenue.txt 是否存在", "score": 5, "max_score": 5, "passed": True, "reason": "文件 midnight_revenue.txt 存在"})
        score += 5
    else:
        details.append({"item": "检查结果文件 midnight_revenue.txt 是否存在", "score": 0, "max_score": 5, "passed": False, "reason": "文件 midnight_revenue.txt 不存在"})
        
    if not file_exists:
        details.append({"item": "检查总收入金额是否正确(12500)", "score": 0, "max_score": 20, "passed": False, "reason": "文件缺失，无法检查"})
        details.append({"item": "检查买家名单是否包含所有正确的购买者", "score": 0, "max_score": 40, "passed": False, "reason": "文件缺失，无法检查"})
        details.append({"item": "检查买家名单是否排除了无关买家", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失，无法检查"})
        details.append({"item": "检查是否排除了每个艺术品的单独报价(LLM)", "score": 0, "max_score": 20, "passed": False, "reason": "文件缺失，无法检查"})
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        content_lower = content.lower()
        # 清除常见的符号和空格，以精确比对数字
        content_clean = content_lower.replace(',', '').replace(' ', '').replace('$', '')
        
        # 3. 检查总收入核心数据 (20分)
        # 通过去噪后的纯文本查找 12500，严禁模糊放行错误数据
        if '12500' in content_clean:
            details.append({"item": "检查总收入金额是否正确(12500)", "score": 20, "max_score": 20, "passed": True, "reason": "文本中精确包含了正确的总金额数值 12500"})
            score += 20
        else:
            details.append({"item": "检查总收入金额是否正确(12500)", "score": 0, "max_score": 20, "passed": False, "reason": "文本中未找到正确的总金额数值(12500)或金额计算有误"})
            
        # 4. 检查正确买家名单是否无遗漏 (40分，每个10分)
        right_buyers = ["alice", "charlie", "eve", "grace"]
        found_right = [b for b in right_buyers if b in content_lower]
        b_score = len(found_right) * 10
        details.append({
            "item": "检查买家名单是否包含所有正确的购买者",
            "score": b_score,
            "max_score": 40,
            "passed": b_score == 40,
            "reason": f"找到了 {len(found_right)}/4 个正确买家: {', '.join(found_right) if found_right else '无'}"
        })
        score += b_score
        
        # 5. 检查是否出现环境幻觉和混入无关买家 (10分)
        wrong_buyers = ["bob", "dave", "frank"]
        found_wrong = [b for b in wrong_buyers if b in content_lower]
        if not found_wrong:
            details.append({
                "item": "检查买家名单是否排除了无关买家",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "未包含无关记录中的买家，数据筛选干净"
            })
            score += 10
        else:
            details.append({
                "item": "检查买家名单是否排除了无关买家",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"混入了属于无关画作的买家: {', '.join(found_wrong)}"
            })
            
        # 6. 利用大模型执行格式的感性与语义审核 (20分)
        # 用户需求 "I can't bear to look at the raw, jagged numbers anymore... Just list the total revenue and the buyers' names clearly."
        prompt_text = "Does the following text ONLY list the combined total revenue and buyer names, and STRICTLY AVOID listing the individual prices of each separate artwork? (If there are individual prices like 2500, 3000, 4500 listed alongside names, say NO. If it's just a grand total and names, say YES.)"
        llm_pass = llm_judge_content(prompt_text, content)
        if llm_pass:
            details.append({
                "item": "利用大模型检查是否排除了每个艺术品的单独报价",
                "score": 20,
                "max_score": 20,
                "passed": True,
                "reason": "大模型判定内容符合 Persona 的艺术感性要求，仅展示汇总而没有罗列单项明细数字"
            })
            score += 20
        else:
            details.append({
                "item": "利用大模型检查是否排除了每个艺术品的单独报价",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": "大模型判定内容中包含了单项数据的罗列，未遵循'不看原始生硬数字'的业务感性需求"
            })

    # 输出统一评分文件
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    work_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(work_dir)
