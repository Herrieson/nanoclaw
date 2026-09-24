import os
import sys
import json
import httpx
from openai import OpenAI

# ==============================================================================
# 配置与初始化
# ==============================================================================
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

# 强制关闭 SSL 验证，初始化客户端
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """
    统一的 LLM 语义检测接口。返回 True / False。
    用于验证自然语言大意与非结构化逻辑。
    """
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

def find_number_in_json(obj, target):
    """
    原生代码严格解析工具：递归遍历任意复杂的 JSON 结构，
    精准寻找特定的目标数值（规避正则表达式带来的不确定性）。
    """
    if isinstance(obj, dict):
        return any(find_number_in_json(v, target) for v in obj.values())
    elif isinstance(obj, list):
        return any(find_number_in_json(v, target) for v in obj)
    elif isinstance(obj, (int, float)):
        return obj == target
    elif isinstance(obj, str):
        # 兼容例如 "24,260" 这样的字符串数字格式
        cleaned_str = obj.replace(",", "")
        return str(target) in cleaned_str
    return False

# ==============================================================================
# 核心验证逻辑
# ==============================================================================
def verify(workspace):
    score = 0
    details = []
    
    report_path = os.path.join(workspace, "deliverables", "audit_report.json")
    
    # [1] 物理探针：目录与文件存在性 (10分)
    if os.path.exists(report_path):
        score += 10
        details.append({"item": "检查交付物 audit_report.json 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "报告文件存在，满足初步交付需求。"})
    else:
        details.append({"item": "检查交付物 audit_report.json 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "关键交付物缺失，后续检查中断。"})
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": score, "details": details}, f, ensure_ascii=False, indent=2)
        return

    # [2] 代码严格解析：格式与 Schema 合法性 (10分)
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            raw_content = f.read()
            report_data = json.loads(raw_content)
        score += 10
        details.append({"item": "检查 JSON 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "报告是合乎规范的结构化 JSON。"})
    except json.JSONDecodeError:
        details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 无法解析，存在语法错误或非结构化残留。"})
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": score, "details": details}, f, ensure_ascii=False, indent=2)
        return

    # [3] 代码严格解析：精确计算提取 (20分)
    # 合规资产计算要求精确无误（150*10 + 320*8 + 6500*2 + 450*12 + 120*15 = 24260）
    if find_number_in_json(report_data, 24260) or find_number_in_json(report_data, 24260.0):
        score += 20
        details.append({"item": "严格解析：合规总价值校验", "score": 20, "max_score": 20, "passed": True, "reason": "成功查找到精确计算值 24260，表明筛选计算无幻觉。"})
    else:
        details.append({"item": "严格解析：合规总价值校验", "score": 0, "max_score": 20, "passed": False, "reason": "未能找到正确的合规总价值 (24260)，存在计算失误、遗漏合规木材或混淆异常物品。"})

    # [4] LLM 语义检测：不合规项目与抗噪分析 (20分)
    prompt_non_compliant = (
        "Check if this JSON explicitly lists 'Pine' (or its ID 'ID_005') as a non-compliant item because it completely lacks a literary code. "
        "Crucially, make sure 'Cement' (ID_002) and the pending item (ID_003) are correctly filtered out from being processed as valid wood altogether (they shouldn't be erroneously labeled as 'non-compliant missing code items', but just ignored as irrelevant). "
        "Answer YES only if Pine is correctly identified and the others are correctly excluded from the core wood processing logic."
    )
    if llm_judge_content(prompt_non_compliant, raw_content):
        score += 20
        details.append({"item": "LLM 语义分析：准确识别不合规项目", "score": 20, "max_score": 20, "passed": True, "reason": "精确识别出 Pine(ID_005) 缺乏编码，且有效排除了不相关类目与未入库状态物品。"})
    else:
        details.append({"item": "LLM 语义分析：准确识别不合规项目", "score": 0, "max_score": 20, "passed": False, "reason": "不合规清单包含幻觉，或未排除水泥、处于 Pending 状态的错误项。"})

    # [5] LLM 语义检测：动态预警报告生成 (20分)
    prompt_warning = (
        "Check if the JSON contains a dedicated section, object, or array specifically for 'dynamic alerts' or 'price warnings'. "
        "It MUST explicitly state that 'Ebony' (or 'ID_006') triggered a warning for exceeding its dynamic threshold price. "
        "Answer YES if such a warning mechanism and specific record exist."
    )
    if llm_judge_content(prompt_warning, raw_content):
        score += 20
        details.append({"item": "LLM 语义分析：触发动态预警明细", "score": 20, "max_score": 20, "passed": True, "reason": "报告正确体现了动态阈值判断，并成功记录了溢价木材（Ebony）的警告。"})
    else:
        details.append({"item": "LLM 语义分析：触发动态预警明细", "score": 0, "max_score": 20, "passed": False, "reason": "报告缺失对超出阈值项目的有效警告记录。"})

    # [6] LLM 语义检测：文化创意产业领域“风格/骨架”判定 (20分)
    prompt_literary = (
        "Does the content of this JSON explicitly exhibit a 'literary skeleton' as requested? "
        "Are literary codes like 'DQ01' or 'HD05' mapped to the inventory, or are there literary concepts/keys (like 'narrative', 'chapter', 'literary_mapping') included? "
        "Answer YES if the data incorporates literary codes or terms aligning with the context."
    )
    if llm_judge_content(prompt_literary, raw_content):
        score += 20
        details.append({"item": "LLM 语义分析：文学骨架与特定代码映射", "score": 20, "max_score": 20, "passed": True, "reason": "成果中深度融合了所需的文学代码体系或文学结构，风格符合设定。"})
    else:
        details.append({"item": "LLM 语义分析：文学骨架与特定代码映射", "score": 0, "max_score": 20, "passed": False, "reason": "未能将业务数据和文学编码有效映射，报告显得僵硬枯燥。"})

    # 结果回写
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": score, "details": details}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    work_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(work_dir)
