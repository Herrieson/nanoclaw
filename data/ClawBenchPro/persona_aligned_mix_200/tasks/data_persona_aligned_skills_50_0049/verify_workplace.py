import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，必须关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    # 此函数为检测非结构化文本的统一接口
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
    report_path = os.path.join(workspace, "bug_report", "culprit_symbol.txt")
    
    score = 0
    details = []
    
    # 1. 检测目标文件与目录是否存在 (10分)
    if os.path.exists(report_path):
        details.append({"item": "检查目标文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "找到了 bug_report/culprit_symbol.txt"})
        score += 10
    else:
        details.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 culprit_symbol.txt，工作区产出不完整"})
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": score, "details": details}, f, indent=2, ensure_ascii=False)
        return

    # 2. 读取内容并检测非空 (10分)
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
    except Exception as e:
        details.append({"item": "文件读取性", "score": 0, "max_score": 10, "passed": False, "reason": f"文件无法读取: {str(e)}"})
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": score, "details": details}, f, indent=2, ensure_ascii=False)
        return

    if not content:
        details.append({"item": "文件内容有效性", "score": 0, "max_score": 10, "passed": False, "reason": "文件为空"})
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": score, "details": details}, f, indent=2, ensure_ascii=False)
        return
        
    details.append({"item": "文件内容有效性", "score": 10, "max_score": 10, "passed": True, "reason": "文件内容不为空"})
    score += 10

    # 3. 内容格式合规性检查：是否按要求提供了无括号的纯粹函数名 (20分)
    is_pure_format = False
    if len(content) < 50 and "(" not in content and ")" not in content and " " not in content:
        is_pure_format = True
        details.append({"item": "纯文本格式规范", "score": 20, "max_score": 20, "passed": True, "reason": "未包含括号、空格或冗余长篇大论，符合纯符号名规范"})
        score += 20
    else:
        details.append({"item": "纯文本格式规范", "score": 0, "max_score": 20, "passed": False, "reason": "包含了括号、多余空格或解释性文本，未能严格遵循纯粹符号名要求"})

    # 4. 确定性提取：是否命中了核心目标函数 `update_hardware_watchdog` (40分)
    target_symbol = "update_hardware_watchdog"
    is_matched = False
    if target_symbol in content:
        is_matched = True
        details.append({"item": "精准命中关键符号", "score": 40, "max_score": 40, "passed": True, "reason": f"成功识别出因DCE误杀丢失的符号: {target_symbol}"})
        score += 40
    else:
        details.append({"item": "精准命中关键符号", "score": 0, "max_score": 40, "passed": False, "reason": "未找到正确的罪魁祸首函数符号"})

    # 5. LLM 防御性校验 / 幻觉检测 (20分)
    # 对于纯粹的精确匹配直接给满分；如果有大量解释文本，动用 LLM 检查它是否捏造了其他函数，或者模棱两可。
    if is_pure_format and is_matched:
        details.append({"item": "语义排爆与幻觉检验", "score": 20, "max_score": 20, "passed": True, "reason": "内容高度纯粹且精准匹配，通过防御性校验"})
        score += 20
    else:
        prompt = (
            "Determine if the user's report unambiguously identifies 'update_hardware_watchdog' "
            "as the ONLY specific culprit function responsible for the watchdog timeout/bug. "
            "If the report is ambiguous, hallucinates other functions as culprits, or lists it merely as a guess among multiple options, answer NO. "
            "Otherwise, answer YES."
        )
        llm_pass = llm_judge_content(prompt, content)
        if llm_pass and is_matched:
            details.append({"item": "语义排爆与幻觉检验", "score": 20, "max_score": 20, "passed": True, "reason": "LLM 判定分析结果明确指出了正确的核心符号，未发生严重幻觉串账"})
            score += 20
        else:
            details.append({"item": "语义排爆与幻觉检验", "score": 0, "max_score": 20, "passed": False, "reason": "LLM 判定报告对核心函数指向不明，或者捏造了不存在的错误"})

    # 写入最终结果
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
