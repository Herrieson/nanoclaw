import os
import sys
import json
import re
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
    billing_ready_dir = os.path.join(workspace, "billing_ready")
    
    score_details = []
    total_score = 0
    
    # 1. 检查目录 (10分)
    if os.path.isdir(billing_ready_dir):
        score_details.append({"item": "检查结果目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录 billing_ready 存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查结果目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录 billing_ready 不存在"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 读取所有文件内容
    files_in_dir = os.listdir(billing_ready_dir)
    all_text = ""
    csv_text = ""
    
    for fname in files_in_dir:
        fpath = os.path.join(billing_ready_dir, fname)
        if os.path.isfile(fpath):
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    all_text += content + "\n"
                    if fname.endswith(".csv"):
                        csv_text += content + "\n"
            except Exception:
                pass

    # 2. 结果文件非空检查 (5分)
    if all_text.strip():
        score_details.append({"item": "结果文件有效性", "score": 5, "max_score": 5, "passed": True, "reason": "在 billing_ready 目录下生成了有效文件。"})
        total_score += 5
    else:
        score_details.append({"item": "结果文件有效性", "score": 0, "max_score": 5, "passed": False, "reason": "目录为空或文件无内容。"})

    # 逐行统计各病人+对应代码的出现次数
    smith_92521 = 0
    miller_92523 = 0
    miller_92507 = 0
    wilson_92610 = 0
    
    for line in all_text.split('\n'):
        line_lower = line.lower()
        if "smith" in line_lower and "92521" in line_lower:
            smith_92521 += 1
        if "miller" in line_lower and "92523" in line_lower:
            miller_92523 += 1
        if "miller" in line_lower and "92507" in line_lower:
            miller_92507 += 1
        if "wilson" in line_lower and "92610" in line_lower:
            wilson_92610 += 1

    # 3. 保留合法数据检查 (15分)
    if smith_92521 >= 1 and miller_92523 >= 1 and miller_92507 >= 1 and wilson_92610 >= 1:
        score_details.append({"item": "合法数据保留验证", "score": 15, "max_score": 15, "passed": True, "reason": "成功提取并保留了所有授权的合法记录。"})
        total_score += 15
    else:
        score_details.append({"item": "合法数据保留验证", "score": 0, "max_score": 15, "passed": False, "reason": "部分或全部合法记录丢失（如未能匹配白名单或被错误过滤）。"})

    # 4. 数据去重检查 (15分)
    # 优先在 csv 内判定去重（防御 Agent 在总结中啰嗦导致假阴性）；若未生成 csv 则在全文本中判定
    target_dedup_text = csv_text if csv_text.strip() else all_text
    smith_92521_target = 0
    miller_92523_target = 0
    for line in target_dedup_text.split('\n'):
        line_lower = line.lower()
        if "smith" in line_lower and "92521" in line_lower:
            smith_92521_target += 1
        if "miller" in line_lower and "92523" in line_lower:
            miller_92523_target += 1
            
    if smith_92521_target == 1 and miller_92523_target == 1:
        score_details.append({"item": "冗余记录去重验证", "score": 15, "max_score": 15, "passed": True, "reason": "成功清理了重复记录，且无冗余输出。"})
        total_score += 15
    else:
        score_details.append({"item": "冗余记录去重验证", "score": 0, "max_score": 15, "passed": False, "reason": f"未正确去重。目标文件中 Smith(92521) 出现 {smith_92521_target} 次，Miller(92523) 出现 {miller_92523_target} 次。"})

    # 5. 总计小时数计算 (20分)
    if "5.5" in all_text:
        score_details.append({"item": "账单总小时数提取", "score": 20, "max_score": 20, "passed": True, "reason": "精准计算出合法的总账单小时数为 5.5。"})
        total_score += 20
    else:
        score_details.append({"item": "账单总小时数提取", "score": 0, "max_score": 20, "passed": False, "reason": "未找到正确的总小时数 '5.5'，计算可能存在逻辑漏洞。"})

    # 6. 未授权病人提取 (15分)
    has_brown = "brown" in all_text.lower()
    has_davis = "davis" in all_text.lower()
    
    if has_brown and has_davis:
        score_details.append({"item": "未授权病人名单识别", "score": 15, "max_score": 15, "passed": True, "reason": "成功识别并列出了因代码错误而被拒的病人 Brown 和 Davis。"})
        total_score += 15
    elif has_brown or has_davis:
        score_details.append({"item": "未授权病人名单识别", "score": 7, "max_score": 15, "passed": False, "reason": "只识别出了部分未授权病人。"})
        total_score += 7
    else:
        score_details.append({"item": "未授权病人名单识别", "score": 0, "max_score": 15, "passed": False, "reason": "未能识别出未授权病人。"})

    # 7. 非结构化语义验证 (20分)
    llm_prompt = """
    Check the file content provided. It is expected to contain a brief summary generated by an assistant for a speech-language pathologist.
    Evaluate whether the text meets ALL the following criteria:
    1. It provides a brief summary describing the processed session data.
    2. It explicitly mentions the total billable hours.
    3. It explicitly mentions that patients Brown (or Brown, L.) and Davis (or Davis, M.) were unauthorized or their codes were invalid.
    4. It DOES NOT falsely claim that legitimate patients (like Smith, Wilson, or Miller) are unauthorized.
    If it strictly meets all these criteria, answer YES. Otherwise answer NO.
    """
    
    if all_text.strip():
        llm_result = llm_judge_content(llm_prompt, all_text)
        if llm_result:
            score_details.append({"item": "利用大模型检查语义合规性", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定总结文件满足了所有业务传达需求，无幻觉。"})
            total_score += 20
        else:
            score_details.append({"item": "利用大模型检查语义合规性", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定总结文件存在严重遗漏、误报或语气/结构不符。"})
    else:
        score_details.append({"item": "利用大模型检查语义合规性", "score": 0, "max_score": 20, "passed": False, "reason": "无文本供大模型检测。"})

    # 记录最终分数
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)

if __name__ == "__main__":
    verify()
