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
    统一的 LLM 语义检测接口：用于判定容错性高的非标准结构体及自然语言幻觉
    """
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict data validation assistant. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[Content to Validate]:\n{file_content}"}
            ],
            temperature=0
        )
        answer = response.choices[0].message.content.strip().lower()
        return "yes" in answer
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    total_score = 0
    details = []

    # =====================================================================
    # 1. 验证 OCR 工具的物理副作用 (10分)
    # =====================================================================
    flag_file = os.path.join(workspace, "handwriting_ocr_pro_skill_called.flag")
    if os.path.exists(flag_file):
        score = 10
        total_score += score
        details.append({"item": "OCR Tool Side Effect", "score": score, "max_score": 10, "passed": True, "reason": "成功检测到 handwriting_ocr_pro_skill 的调用痕迹。"})
    else:
        details.append({"item": "OCR Tool Side Effect", "score": 0, "max_score": 10, "passed": False, "reason": "未检测到 handwriting_ocr_pro_skill 被调用的痕迹，可能错过了手写内容的解析。"})

    # =====================================================================
    # 2. 验证结果文件存在及 Schema 格式合法性 (15分)
    # =====================================================================
    report_file = os.path.join(workspace, "reports", "final_summary.json")
    json_data = None
    if not os.path.exists(report_file):
        details.append({"item": "Report File Existence", "score": 0, "max_score": 15, "passed": False, "reason": "未找到要求的输出文件 reports/final_summary.json。"})
        # 提前终止，后续基于文件的检查均按失败计
        save_results(total_score, details, workspace)
        return
    else:
        try:
            with open(report_file, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            score = 15
            total_score += score
            details.append({"item": "Report File Existence & Valid JSON", "score": score, "max_score": 15, "passed": True, "reason": "文件存在且 JSON 结构合法。"})
        except json.JSONDecodeError:
            details.append({"item": "Report File Existence & Valid JSON", "score": 0, "max_score": 15, "passed": False, "reason": "文件存在但无法解析为标准的 JSON 格式。"})
            save_results(total_score, details, workspace)
            return

    # =====================================================================
    # 3. 验证必需的三大顶层字段存在 (15分)
    # =====================================================================
    required_keys = ["unauthorized_workers", "approved_summary", "total_pillars_damaged"]
    missing_keys = [k for k in required_keys if k not in json_data]
    if not missing_keys:
        score = 15
        total_score += score
        details.append({"item": "Required JSON Keys", "score": score, "max_score": 15, "passed": True, "reason": "成功找到所有必须的顶层键。"})
    else:
        # 部分给分
        found_keys = len(required_keys) - len(missing_keys)
        score = found_keys * 5
        total_score += score
        details.append({"item": "Required JSON Keys", "score": score, "max_score": 15, "passed": False, "reason": f"缺失字段: {missing_keys}"})

    # =====================================================================
    # 4. 精准验证 unauthorized_workers 列表准确性 (20分)
    # =====================================================================
    unauth_list = json_data.get("unauthorized_workers", [])
    if isinstance(unauth_list, list):
        normalized_unauth = [str(x).lower().replace("_", " ").strip() for x in unauth_list]
        expected_unauth = ["jose ghost", "unknown guy"]
        
        # 计算是否精准匹配
        has_jose = any("jose ghost" in x for x in normalized_unauth)
        has_unknown = any("unknown guy" in x for x in normalized_unauth)
        no_extras = len(normalized_unauth) <= 2  # 严禁幻觉
        
        if has_jose and has_unknown and no_extras:
            score = 20
            total_score += score
            details.append({"item": "Unauthorized Workers Accuracy", "score": score, "max_score": 20, "passed": True, "reason": "准确提取了所有的非法/未授权工人且无捏造。"})
        elif has_jose or has_unknown:
            score = 10
            total_score += score
            details.append({"item": "Unauthorized Workers Accuracy", "score": score, "max_score": 20, "passed": False, "reason": "部分提取了未授权工人或存在幻觉多余人员。"})
        else:
            details.append({"item": "Unauthorized Workers Accuracy", "score": 0, "max_score": 20, "passed": False, "reason": "未提取出任何期望的未授权工人。"})
    else:
        details.append({"item": "Unauthorized Workers Accuracy", "score": 0, "max_score": 20, "passed": False, "reason": "unauthorized_workers 不是列表格式。"})

    # =====================================================================
    # 5. 精准验证 total_pillars_damaged 数值 (10分)
    # =====================================================================
    total_dmg = json_data.get("total_pillars_damaged", None)
    # 根据业务逻辑，如果是只计算合规人员为7；如果是所有记录的总量为8。两者均算正确。
    if str(total_dmg).strip() in ["7", "8"]:
        score = 10
        total_score += score
        details.append({"item": "Total Pillars Damaged", "score": score, "max_score": 10, "passed": True, "reason": f"总柱子损耗数量正确 ({total_dmg})。"})
    else:
        details.append({"item": "Total Pillars Damaged", "score": 0, "max_score": 10, "passed": False, "reason": f"总损耗数量不正确，当前值为: {total_dmg}，期望值为 7 或 8。"})

    # =====================================================================
    # 6. LLM 柔性验证 approved_summary 的复杂数据分布 (30分)
    # =====================================================================
    # 由于 Agent 提取 JSON 字典时对于嵌套字段的命名不可控(如 {"Mateo Hernandez": {"hours": 12, "broken": 3}})，
    # 使用纯代码提取容易造成大量假阴性。此处引入 LLM 执行柔性及抗毁验证，确保没有混入非法工人且数值大体正确。
    approved_summary = json_data.get("approved_summary", {})
    
    if not approved_summary:
        details.append({"item": "LLM Validation of Approved Summary", "score": 0, "max_score": 30, "passed": False, "reason": "approved_summary 为空。"})
    else:
        prompt = """
        Review the JSON object extracted by an AI. This object maps legitimate construction workers to their total logged hours and damaged pillars.
        Expected approximate data:
        - Mateo Hernandez: ~12 hours, ~3 pillars damaged
        - Luis Rodriguez: ~10 hours, ~0 pillars damaged
        - Santiago Garcia: ~12 hours, ~1 pillar damaged
        - Carlos Martinez: ~8 hours, ~3 pillars damaged
        - Juan Lopez: ~6 hours, ~0 pillars damaged

        CRITICAL CONDITIONS FOR A 'YES':
        1. All 5 legitimate workers above must be represented with roughly the correct numbers. (Some small deviations are tolerated, but cumulative additions like Mateo's 8+4=12 must be evident).
        2. The object MUST NOT contain unauthorized workers such as 'Jose Ghost' or 'Unknown_Guy'.
        3. No hallucinatory metrics should exist (e.g. wages, unrelated material).

        Evaluate strictly. Does the content meet the conditions?
        """
        
        is_valid = llm_judge_content(prompt, json.dumps(approved_summary, ensure_ascii=False))
        if is_valid:
            score = 30
            total_score += score
            details.append({"item": "LLM Validation of Approved Summary", "score": score, "max_score": 30, "passed": True, "reason": "LLM 判定合法人员的工时与材料损耗明细逻辑清晰且无混入非法数据。"})
        else:
            details.append({"item": "LLM Validation of Approved Summary", "score": 0, "max_score": 30, "passed": False, "reason": "LLM 判定 approved_summary 内的数据严重不符（可能存在幻觉、未合并计算或者混入了非法人员）。"})

    save_results(total_score, details, workspace)

def save_results(total_score, details, workspace):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    verify()
