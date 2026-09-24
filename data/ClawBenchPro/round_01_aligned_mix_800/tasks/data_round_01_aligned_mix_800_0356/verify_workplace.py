import os
import sys
import json
import re
import httpx
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
    target_dir = os.path.join(workspace, "family_planning")
    
    score_details = []
    total_score = 0
    
    # 1. 检查目标目录及文件是否存在 (20分)
    file_found = False
    content_merged = ""
    if os.path.exists(target_dir) and os.path.isdir(target_dir):
        files = os.listdir(target_dir)
        if files:
            file_found = True
            for f in files:
                file_path = os.path.join(target_dir, f)
                if os.path.isfile(file_path):
                    with open(file_path, "r", encoding="utf-8") as fp:
                        content_merged += fp.read() + "\n"
                        
    if file_found and content_merged.strip():
        score_details.append({"item": "检查目标输出目录和文件是否成功生成", "score": 20, "max_score": 20, "passed": True, "reason": "family_planning 目录下生成了包含内容的文件"})
        total_score += 20
    else:
        score_details.append({"item": "检查目标输出目录和文件是否成功生成", "score": 0, "max_score": 20, "passed": False, "reason": "未在 family_planning 目录下找到有效文件"})
        
    # 2. 精确提取工资计算结果 (代码层级确定性检验) (40分)
    # 因为自然语言可能是英语或西班牙语，金额格式可能为 355.25 或 355,25
    paycheck_passed = False
    if file_found:
        # 提取所有类似于金额的数字
        numbers = re.findall(r'355[.,]25', content_merged)
        if numbers:
            paycheck_passed = True
            score_details.append({"item": "精确检查预期总薪资是否正确计算", "score": 40, "max_score": 40, "passed": True, "reason": f"在文档中精准检测到预期结果 '355.25'"})
            total_score += 40
        else:
            score_details.append({"item": "精确检查预期总薪资是否正确计算", "score": 0, "max_score": 40, "passed": False, "reason": "未在文档中检测到正确的薪资数字 355.25，可能是计算错误（没有扣除休息时间或解析失败）"})
    else:
         score_details.append({"item": "精确检查预期总薪资是否正确计算", "score": 0, "max_score": 40, "passed": False, "reason": "文件不存在，无法检查薪资"})

    # 3. LLM 语义检测：核对冲突的日期并检查幻觉捏造 (40分)
    if file_found:
        prompt_text = """Analyze the provided document written by the Agent.
Check if the document accurately states the following conflicting Thursday dates: October 12 (2023-10-12) and October 26 (2023-10-26).
Also, ensure the document DOES NOT fabricate any other random dates or additional shifts that weren't in the context.
If it accurately identifies the two dates and has no hallucinations, answer YES. Otherwise, answer NO."""
        
        llm_passed = llm_judge_content(prompt_text, content_merged)
        if llm_passed:
            score_details.append({"item": "利用大模型检查日期语义及是否存在幻觉", "score": 40, "max_score": 40, "passed": True, "reason": "大模型判定冲突日期识别准确，且无捏造信息"})
            total_score += 40
        else:
            score_details.append({"item": "利用大模型检查日期语义及是否存在幻觉", "score": 0, "max_score": 40, "passed": False, "reason": "大模型判定未正确指出冲突日期，或存在捏造的虚假信息"})
    else:
        score_details.append({"item": "利用大模型检查日期语义及是否存在幻觉", "score": 0, "max_score": 40, "passed": False, "reason": "文件不存在，无法进行语义检查"})

    # 输出最终评测报告
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
