import os
import sys
import json
import re
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
    report_dir = os.path.join(workspace, "final_report")
    score_file = os.path.join(workspace, "workplace_score.json")

    total_score = 0
    details = []

    # 1. 结构验证: 检查目录是否存在
    dir_exists = os.path.isdir(report_dir)
    if dir_exists:
        details.append({"item": "检查结果目录 `final_report` 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录 final_report 存在"})
        total_score += 10
    else:
        details.append({"item": "检查结果目录 `final_report` 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 `final_report` 目录"})

    # 2. 结构验证: 检查文件是否存在并合并提取内容
    content = ""
    if dir_exists:
        try:
            files = os.listdir(report_dir)
            valid_files = [f for f in files if os.path.isfile(os.path.join(report_dir, f))]
            if valid_files:
                details.append({"item": "检查目录下是否生成了总结文件", "score": 10, "max_score": 10, "passed": True, "reason": f"找到文件: {', '.join(valid_files)}"})
                total_score += 10
                # 读取所有文件内容用于后续判定
                for vf in valid_files:
                    try:
                        with open(os.path.join(report_dir, vf), "r", encoding="utf-8") as f:
                            content += f.read() + "\n"
                    except:
                        pass
            else:
                details.append({"item": "检查目录下是否生成了总结文件", "score": 0, "max_score": 10, "passed": False, "reason": "目录为空，无总结文件"})
        except Exception as e:
            details.append({"item": "检查目录下是否生成了总结文件", "score": 0, "max_score": 10, "passed": False, "reason": f"读取目录失败: {e}"})
    else:
        details.append({"item": "检查目录下是否生成了总结文件", "score": 0, "max_score": 10, "passed": False, "reason": "由于目录不存在，无法检查文件"})

    # 3. 数据验证: 核心计算精确提取
    if content.strip():
        # 总收入(cleared): 500+300(wk1) + 1000+2000(wk2) = 3800
        # 总支出: 800+350 = 1150 (50的church permit不计入)
        # 最终正确余额 = 3800 - 1150 = 2650
        if re.search(r"2,?650(?:\.00)?", content):
            details.append({"item": "验证最终余额 2650 的绝对数值准确性", "score": 30, "max_score": 30, "passed": True, "reason": "成功在报告中匹配到正确计算结果 2650"})
            total_score += 30
        else:
            details.append({"item": "验证最终余额 2650 的绝对数值准确性", "score": 0, "max_score": 30, "passed": False, "reason": "报告中未能找到正确的最终结果 2650，逻辑计算存在严重偏差"})
            
        # 4. 数据验证: 排除典型错算干扰项
        error_found = []
        if re.search(r"2,?600(?:\.00)?", content):
            error_found.append("2600 (误扣减了本应由教堂支付的50元许可证费)")
        if re.search(r"3,?100(?:\.00)?", content):
            error_found.append("3100 (未排除无效退票或取消的捐款款项)")
        
        if not error_found:
            details.append({"item": "检查是否排除了典型错误计算干扰项", "score": 10, "max_score": 10, "passed": True, "reason": "没有发现典型的错算金额（如2600或3100），数据清洗可靠"})
            total_score += 10
        else:
            details.append({"item": "检查是否排除了典型错误计算干扰项", "score": 0, "max_score": 10, "passed": False, "reason": f"发现了因业务理解错误导致的错算结果: {', '.join(error_found)}"})

        # 5. LLM 语义验证: 明确表达最终余额
        prompt_balance = "Does the text clearly state that the final true balance, total funds collected, or final remaining money is exactly 2650? It should not just be a random number in a list, but explicitly described as the final true amount after expenses."
        passed_balance = llm_judge_content(prompt_balance, content)
        if passed_balance:
            details.append({"item": "利用大模型检查语境是否明确指出 2650 为最终结余", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定内容中 2650 明确被指代为最终结余，非随机数字或偶然命中"})
            total_score += 20
        else:
            details.append({"item": "利用大模型检查语境是否明确指出 2650 为最终结余", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定虽有数字存在，但语义上未指明这是最终的计算余额，可能存在幻觉敷衍"})

        # 6. LLM 语义验证: 格式简单，无复杂代码杂糅，符合 Persona
        prompt_format = "Is the text a clean, simple summary ready to be printed and shown to a Pastor? It MUST NOT contain any confusing computer code (like Python scripts, print statements), complex JSON syntax, or highly technical jargon. Answer YES if it is clean and highly readable for a layman, NO if it contains code or complex markdown tables."
        passed_format = llm_judge_content(prompt_format, content)
        if passed_format:
            details.append({"item": "利用大模型检查报告格式是否满足 Persona 要求（无代码，直白易读）", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定报告格式干净简单，无代码杂音，完全契合建筑工人的背景需求"})
            total_score += 20
        else:
            details.append({"item": "利用大模型检查报告格式是否满足 Persona 要求（无代码，直白易读）", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定报告中包含了复杂的代码执行记录或技术型语法，未考虑用户的弱计算机基础"})

    else:
        details.append({"item": "验证最终余额 2650 的绝对数值准确性", "score": 0, "max_score": 30, "passed": False, "reason": "未找到总结文件内容，无法提取"})
        details.append({"item": "检查是否排除了典型错误计算干扰项", "score": 0, "max_score": 10, "passed": False, "reason": "未找到总结文件内容，无法核查"})
        details.append({"item": "利用大模型检查语境是否明确指出 2650 为最终结余", "score": 0, "max_score": 20, "passed": False, "reason": "未找到总结文件内容，无法核查"})
        details.append({"item": "利用大模型检查报告格式是否满足 Persona 要求", "score": 0, "max_score": 20, "passed": False, "reason": "未找到总结文件内容，无法核查"})

    # 汇总输出
    result = {
        "total_score": total_score,
        "details": details
    }

    with open(score_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
