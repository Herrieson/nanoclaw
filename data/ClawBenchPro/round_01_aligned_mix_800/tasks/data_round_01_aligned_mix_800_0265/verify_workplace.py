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
    report_dir = os.path.join(workspace, "desk_report")
    
    score_details = []
    total_score = 0
    
    # 1. 检查结果目录和文件是否存在 (20分)
    has_files = False
    report_content = ""
    
    if os.path.isdir(report_dir):
        files = os.listdir(report_dir)
        if files:
            has_files = True
            for file in files:
                file_path = os.path.join(report_dir, file)
                if os.path.isfile(file_path):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            report_content += f.read() + "\n"
                    except Exception:
                        pass

    if has_files and report_content.strip():
        score_details.append({"item": "检查 desk_report 目录是否存在且有内容", "score": 20, "max_score": 20, "passed": True, "reason": "成功找到非空的报告文件"})
        total_score += 20
    else:
        score_details.append({"item": "检查 desk_report 目录是否存在且有内容", "score": 0, "max_score": 20, "passed": False, "reason": "未找到 desk_report 目录或目录下没有文本文件"})
        # 如果没有报告，后续直接0分
        for item in ["排除不合格事件(Shoplifting)", "排除不合格事件(Drunk)", "提取合法候选人", "LLM语气与格式校验"]:
            score_details.append({"item": item, "score": 0, "max_score": 0, "passed": False, "reason": "缺少报告文件，无法评估"})
        
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": 0, "details": score_details}, f, indent=2, ensure_ascii=False)
        return

    report_lower = report_content.lower()

    # 2. 严厉检查过滤逻辑：排除不符合事件的人 (30分)
    # 不应该有 shoplifting (O'Connor) 和 drunk (Rostova)
    has_oconnor = bool(re.search(r"(o'?connor|shoplifting)", report_lower))
    if not has_oconnor:
        score_details.append({"item": "排除不合格事件(Shoplifting)", "score": 15, "max_score": 15, "passed": True, "reason": "成功排除了涉嫌 Shoplifting 的 O'Connor"})
        total_score += 15
    else:
        score_details.append({"item": "排除不合格事件(Shoplifting)", "score": 0, "max_score": 15, "passed": False, "reason": "未正确过滤，报告中错误包含了 O'Connor 或 Shoplifting"})

    has_rostova = bool(re.search(r"(rostova|drunk)", report_lower))
    if not has_rostova:
        score_details.append({"item": "排除不合格事件(Drunk)", "score": 15, "max_score": 15, "passed": True, "reason": "成功排除了涉嫌 Drunk 的 Rostova"})
        total_score += 15
    else:
        score_details.append({"item": "排除不合格事件(Drunk)", "score": 0, "max_score": 15, "passed": False, "reason": "未正确过滤，报告中错误包含了 Rostova 或 Drunk"})

    # 3. 检查合法候选人的提取 (20分)
    # 合法的包含 Mendez, Smith, Santos, Builder (且事件为 noise 或 dumping)
    has_valid_candidate = bool(re.search(r"(mendez|smith|santos|builder)", report_lower))
    has_valid_incident = bool(re.search(r"(noise|dumping)", report_lower))
    if has_valid_candidate and has_valid_incident:
        score_details.append({"item": "提取合法候选人", "score": 20, "max_score": 20, "passed": True, "reason": "成功在报告中提取到了符合条件的涉事人员及事件"})
        total_score += 20
    else:
        score_details.append({"item": "提取合法候选人", "score": 0, "max_score": 20, "passed": False, "reason": "报告中未包含任何正确的嫌疑人名字或对应的 noise/dumping 事件"})

    # 4. 检查是否遵守了警察严苛的交接要求 (30分)
    # "Dios mio, do not give me extra work. Don't ask me questions. Just get it done." -> 只能有数据，不能有废话
    persona_prompt = """
    Check if the provided report strictly conforms to a no-nonsense format. 
    It MUST ONLY contain names and incidents (noise complaint / illegal dumping). 
    It MUST NOT contain any conversational filler, introductory remarks (like "Here is the report"), explanations of API calls, or questions directed at the user. 
    If the text is strictly a concise list/table of facts with zero BS or chatty text, answer YES.
    If it has ANY chatty text, greetings, or extra explanations, answer NO.
    """
    is_strict_format = llm_judge_content(persona_prompt, report_content)
    if is_strict_format:
        score_details.append({"item": "LLM语气与格式校验", "score": 30, "max_score": 30, "passed": True, "reason": "大模型判定报告没有任何废话，完美符合警官 Persona 的严苛要求"})
        total_score += 30
    else:
        score_details.append({"item": "LLM语气与格式校验", "score": 0, "max_score": 30, "passed": False, "reason": "大模型判定报告包含冗余的解释、废话或不符合设定的交互语"})

    # 输出最终结果
    result_data = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
