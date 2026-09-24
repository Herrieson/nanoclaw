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
    """
    此函数为检测非结构化文本的统一接口。
    严格限制输出为 YES 或 NO，消除正则匹配带来的幻觉或误判。
    """
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict data validation assistant. Answer ONLY with 'YES' or 'NO'. Read the text carefully and be extremely precise with numbers and names."},
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
    audit_dir = os.path.join(workspace, "audit_results")
    
    score = 0
    details = []
    
    # ---------------------------------------------------------
    # 1. 目录结构与数据存在性验证 (原生代码层)
    # ---------------------------------------------------------
    if os.path.isdir(audit_dir):
        score += 10
        details.append({"item": "检查目标结果目录 audit_results 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "成功创建 audit_results 目录"})
    else:
        details.append({"item": "检查目标结果目录 audit_results 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 audit_results 目录"})
        
    content = ""
    file_count = 0
    json_csv_valid = True
    
    if os.path.isdir(audit_dir):
        for root, _, files in os.walk(audit_dir):
            for f in files:
                file_count += 1
                file_path = os.path.join(root, f)
                # 可选：如果 Agent 输出了标准格式，验证其 Schema 合法性
                if f.endswith('.json'):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as jf:
                            json.load(jf)
                    except:
                        json_csv_valid = False
                try:
                    with open(file_path, 'r', encoding='utf-8') as f_in:
                        content += f"\n--- File: {f} ---\n{f_in.read()}"
                except:
                    pass
                    
    if file_count > 0 and json_csv_valid:
        score += 10
        details.append({"item": "检查结果文件是否生成及结构化文件(若有)格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": f"找到了 {file_count} 个结果文件，且格式验证通过"})
    elif file_count > 0 and not json_csv_valid:
        details.append({"item": "检查结果文件是否生成及结构化文件(若有)格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": "生成了文件，但发现损坏的 JSON/CSV 文件格式"})
    else:
        details.append({"item": "检查结果文件是否生成及结构化文件(若有)格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": "目录为空，未找到任何结果文件"})

    # 若没有文件，提前结算
    if file_count == 0:
        for item in ["Robert Brown欠费", "Emily Davis欠费", "发现幽灵 Unknown_Entity_X", "发现幽灵 Zodiac_Alpha", "理论总收入", "实际总收入", "无幻觉校验"]:
            details.append({"item": item, "score": 0, "max_score": 10, "passed": False, "reason": "缺失内容无法评估"})
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": score, "details": details}, f, ensure_ascii=False, indent=2)
        return

    # ---------------------------------------------------------
    # 2. 细粒度业务逻辑验证 (LLM 语义层 - 严格匹配)
    # ---------------------------------------------------------
    
    # 验证欠款情况：Robert Brown
    prompt_rb = "Does the report correctly and explicitly identify that 'Robert Brown' underpaid by exactly $300 (or 300)?"
    if llm_judge_content(prompt_rb, content):
        score += 10
        details.append({"item": "Robert Brown欠费记录", "score": 10, "max_score": 10, "passed": True, "reason": "精准定位到 Robert Brown 欠费 300"})
    else:
        details.append({"item": "Robert Brown欠费记录", "score": 0, "max_score": 10, "passed": False, "reason": "未能准确指出 Robert Brown 欠费金额 300"})

    # 验证欠款情况：Emily Davis
    prompt_ed = "Does the report correctly and explicitly identify that 'Emily Davis' missed a payment or has a deficit of exactly $1800 (or 1800)?"
    if llm_judge_content(prompt_ed, content):
        score += 10
        details.append({"item": "Emily Davis欠费记录", "score": 10, "max_score": 10, "passed": True, "reason": "精准定位到 Emily Davis 欠费 1800"})
    else:
        details.append({"item": "Emily Davis欠费记录", "score": 0, "max_score": 10, "passed": False, "reason": "未能准确指出 Emily Davis 欠费金额 1800"})

    # 验证幽灵名单：Unknown_Entity_X
    prompt_ue = "Does the report explicitly name 'Unknown_Entity_X' as someone who paid but is not on the master lease (a ghost/unrecognized payee)?"
    if llm_judge_content(prompt_ue, content):
        score += 10
        details.append({"item": "发现幽灵 Unknown_Entity_X", "score": 10, "max_score": 10, "passed": True, "reason": "成功找出不在名册内的 Unknown_Entity_X"})
    else:
        details.append({"item": "发现幽灵 Unknown_Entity_X", "score": 0, "max_score": 10, "passed": False, "reason": "漏掉幽灵名单 Unknown_Entity_X"})

    # 验证幽灵名单：Zodiac_Alpha
    prompt_za = "Does the report explicitly name 'Zodiac_Alpha' as someone who paid but is not on the master lease (a ghost/unrecognized payee)?"
    if llm_judge_content(prompt_za, content):
        score += 10
        details.append({"item": "发现幽灵 Zodiac_Alpha", "score": 10, "max_score": 10, "passed": True, "reason": "成功找出不在名册内的 Zodiac_Alpha"})
    else:
        details.append({"item": "发现幽灵 Zodiac_Alpha", "score": 0, "max_score": 10, "passed": False, "reason": "漏掉幽灵名单 Zodiac_Alpha"})

    # 验证财务对账：理论预期总收入 (12300 * 3 = 36900)
    prompt_tr = "Does the report explicitly state that the 'Theoretical Revenue' (or expected revenue for Q1 based on leases) is exactly 36900 or 36,900?"
    if llm_judge_content(prompt_tr, content):
        score += 15
        details.append({"item": "理论总收入验证", "score": 15, "max_score": 15, "passed": True, "reason": "正确算出理论总收入 36900"})
    else:
        details.append({"item": "理论总收入验证", "score": 0, "max_score": 15, "passed": False, "reason": "理论总收入数值错误或未给出"})

    # 验证财务对账：实际进账总收入 (36900 - 2100 + 2600 = 37400)
    prompt_ar = "Does the report explicitly state that the 'Actual Revenue' (or collected revenue for Q1) is exactly 37400 or 37,400?"
    if llm_judge_content(prompt_ar, content):
        score += 15
        details.append({"item": "实际总收入验证", "score": 15, "max_score": 15, "passed": True, "reason": "正确算出实际总收入 37400"})
    else:
        details.append({"item": "实际总收入验证", "score": 0, "max_score": 15, "passed": False, "reason": "实际总收入数值错误或未给出"})

    # ---------------------------------------------------------
    # 3. 幻觉与欺骗探测 (防作弊核心)
    # ---------------------------------------------------------
    prompt_hall = "Are 'Robert Brown' and 'Emily Davis' the ONLY tenants listed with deficits, AND are 'Unknown_Entity_X' and 'Zodiac_Alpha' the ONLY ghosts listed? Answer 'YES' if there are strictly NO other false findings, extra ghost names, or extra deficit reports. Answer 'NO' if the report contains extra/false deficit warnings or ghosts."
    if llm_judge_content(prompt_hall, content):
        score += 10
        details.append({"item": "无幻觉与无作弊校验", "score": 10, "max_score": 10, "passed": True, "reason": "未报告多余的错误欠费或虚假幽灵记录，数据极其干净"})
    else:
        details.append({"item": "无幻觉与无作弊校验", "score": 0, "max_score": 10, "passed": False, "reason": "报告中夹杂了对其他租客的虚假指控或臆造了幽灵名单，严重扣分"})

    # 输出得分文件
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": score, "details": details}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    verify()
