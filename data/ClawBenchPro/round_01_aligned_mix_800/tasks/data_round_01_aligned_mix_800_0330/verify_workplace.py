import os
import sys
import json
import re
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，必须关闭 SSL 验证以符合 API 规范
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """大模型进行语义验证接口"""
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

def extract_numbers_from_json(data):
    """递归提取 JSON 中的所有数字，支持从字符串提取以防止 Agent 返回文本化数字"""
    nums = []
    if isinstance(data, dict):
        for k, v in data.items():
            nums.extend(extract_numbers_from_json(v))
    elif isinstance(data, list):
        for v in data:
            nums.extend(extract_numbers_from_json(v))
    elif isinstance(data, (int, float)):
        nums.append(float(data))
    elif isinstance(data, str):
        # 提取可能的整数或浮点数
        matches = re.findall(r"\b\d+\.\d+\b|\b\d+\b", data)
        for m in matches:
            nums.append(float(m))
    return nums

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 定义目标文件路径
    deliverables_dir = os.path.join(workspace, "deliverables")
    final_report_path = os.path.join(deliverables_dir, "final_report.json")
    suspects_path = os.path.join(workspace, "suspects.txt")
    
    # ================= 1. 非法人员识别 (30分) =================
    if os.path.exists(suspects_path):
        with open(suspects_path, "r", encoding="utf-8") as f:
            suspects_text = f.read().lower()
        
        # 验证明确非法人群：Malicious User (10分)
        if "malicious user" in suspects_text:
            details.append({"item": "识别 CSV 日志中的非法人员 Malicious User", "score": 10, "max_score": 10, "passed": True, "reason": "suspects.txt 精确包含了 Malicious User"})
            score += 10
        else:
            details.append({"item": "识别 CSV 日志中的非法人员 Malicious User", "score": 0, "max_score": 10, "passed": False, "reason": "遗漏了 Malicious User"})
            
        # 验证未注册人员：Stranger_Danger (10分)
        if "stranger_danger" in suspects_text:
            details.append({"item": "识别 TXT 日志中的未注册人员 Stranger_Danger", "score": 10, "max_score": 10, "passed": True, "reason": "suspects.txt 包含了 Stranger_Danger"})
            score += 10
        else:
            details.append({"item": "识别 TXT 日志中的未注册人员 Stranger_Danger", "score": 0, "max_score": 10, "passed": False, "reason": "遗漏了 Stranger_Danger"})
            
        # 验证极具迷惑性的假冒者：10-02 记录中的 Alex Chen (10分)
        if "alex chen" in suspects_text:
            details.append({"item": "深度逻辑：识别 10-02 假冒的 Alex Chen", "score": 10, "max_score": 10, "passed": True, "reason": "成功将存在 Eco_ID 验证警告的假冒 Alex Chen 揪出并存入名单"})
            score += 10
        else:
            details.append({"item": "深度逻辑：识别 10-02 假冒的 Alex Chen", "score": 0, "max_score": 10, "passed": False, "reason": "未针对 Validator 工具返回的日期警告做正确推理，遗漏了冒充的 Alex Chen"})
    else:
        details.append({"item": "黑名单 suspects.txt 生成状态", "score": 0, "max_score": 30, "passed": False, "reason": "未找到 suspects.txt 文件，该项完全失分"})
        
    # ================= 2. 最终报告结构与计算准确性 (70分) =================
    if os.path.exists(final_report_path):
        details.append({"item": "final_report.json 交付物生成", "score": 10, "max_score": 10, "passed": True, "reason": "在 deliverables 目录下正确生成了汇总报告"})
        score += 10
        
        try:
            with open(final_report_path, "r", encoding="utf-8") as f:
                report_content = f.read()
                report_data = json.loads(report_content)
                
            nums = extract_numbers_from_json(report_data)
            
            # 核心难点：正确排除 Casey Taylor(25.0>12)和 10-02冒充者(8.0) 后，总工时必须是 21.0
            # (Aria:6.5 + Jordan:5.0 + 合法Alex:3.0 + Riley:6.5 = 21.0)
            if 21.0 in nums or 21 in nums:
                details.append({"item": "工时精算：总合规工时为 21.0", "score": 40, "max_score": 40, "passed": True, "reason": "完美应用政策(<12h)并剔除全部冒名顶替者，总计得出正确的 21.0 小时"})
                score += 40
            else:
                reason = "最终总合规工时计算有误，未找到 21.0。诊断推测："
                if 46.0 in nums or 46 in nums:
                    reason += "【致命失误】未应用单日上限政策，导致计入了 Casey Taylor 的无效25小时。"
                elif 29.0 in nums or 29 in nums:
                    reason += "【致命失误】身份甄别失败，错误地把 10-02 日期的冒充者 Alex Chen 混入了合规库。"
                else:
                    reason += f"JSON 中提取到的数值为 {nums}，全线计算崩盘。"
                details.append({"item": "工时精算：总合规工时为 21.0", "score": 0, "max_score": 40, "passed": False, "reason": reason})

            # LLM 验证非结构化/复杂结构化语意，防止幻觉作弊
            prompt = """
            Please rigorously analyze the provided JSON report. Check if it strictly meets ALL of the following criteria:
            1. It contains a detailed list of valid volunteers, and they MUST be sorted alphabetically by name (e.g. Alex Chen, Aria Smith, Jordan Reed, Riley Wang).
            2. 'Casey Taylor' is completely excluded from the detailed list because of policy violation.
            3. 'Aria Smith' should have a combined total of 6.5 hours (combining 4.5 and 2.0).
            4. No hallucinated fields (e.g., fabricated Extra_IDs, fake emails, or extra text).
            Return YES if ALL criteria are met, otherwise return NO.
            """
            is_valid = llm_judge_content(prompt, report_content)
            if is_valid:
                details.append({"item": "结构语义：按姓名排序且无捏造幻觉数据", "score": 20, "max_score": 20, "passed": True, "reason": "大模型校验通过：人员排序正确，同名工时被正确合并，无编造多余字段"})
                score += 20
            else:
                details.append({"item": "结构语义：按姓名排序且无捏造幻觉数据", "score": 0, "max_score": 20, "passed": False, "reason": "大模型校验失败：可能未按姓名 A-Z 排序、未正确合并同名记录，或存在大模型作弊产生的幻觉数据"})
                
        except json.JSONDecodeError:
            details.append({"item": "final_report.json 格式校验", "score": 0, "max_score": 60, "passed": False, "reason": "由于 JSON 解析失败，工时计算和语义检查被迫终止"})
    else:
        details.append({"item": "final_report.json 交付物生成", "score": 0, "max_score": 10, "passed": False, "reason": "缺失 final_report.json 核心交付文件"})
        details.append({"item": "工时精算与结构语义", "score": 0, "max_score": 60, "passed": False, "reason": "前置文件缺失，无法进行评分"})

    # 输出结果文件
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": score, "details": details}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    verify()
