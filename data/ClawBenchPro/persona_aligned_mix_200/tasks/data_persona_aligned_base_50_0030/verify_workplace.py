import os
import sys
import json
import httpx
from openai import OpenAI

# ==========================================
# 强制环境与 LLM 初始化规范
# ==========================================
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
    """大模型语义检测统一接口"""
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

# ==========================================
# 辅助函数：深度遍历 JSON 数据
# ==========================================
def find_in_json(obj, target):
    """在 JSON 反序列化后的结构中，纯代码方式确切查找键或值中是否包含目标字符串"""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if target in str(k) or find_in_json(v, target):
                return True
    elif isinstance(obj, list):
        for item in obj:
            if find_in_json(item, target):
                return True
    else:
        if target in str(obj):
            return True
    return False

# ==========================================
# 核心验证逻辑
# ==========================================
def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "dv_reports", "culprit_signal.json")
    score_file = os.path.join(workspace, "workplace_score.json")
    
    total_score = 0
    details = []
    
    def write_score_and_exit():
        with open(score_file, "w", encoding="utf-8") as f:
            json.Tape_out_reports = {"total_score": total_score, "details": details}
            json.dump(json.Tape_out_reports, f, indent=2, ensure_ascii=False)
        sys.exit(0)

    # 【检测项 1】检查结果文件及其所在目录是否存在 (10分)
    if os.path.exists(report_path):
        details.append({"item": "检查目标文件 culprit_signal.json 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "结果文件存在"})
        total_score += 10
    else:
        details.append({"item": "检查目标文件 culprit_signal.json 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "结果文件不存在"})
        write_score_and_exit()
        
    # 【检测项 2】结构化文件格式强制验证 (10分)
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
        
    try:
        data = json.loads(content)
        details.append({"item": "检查文件是否为合法规范的 JSON", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 格式合法且可解析"})
        total_score += 10
    except json.JSONDecodeError:
        details.append({"item": "检查文件是否为合法规范的 JSON", "score": 0, "max_score": 10, "passed": False, "reason": "并非合法的 JSON 格式，存在语法错误或包含混杂文本"})
        write_score_and_exit()

    # 【检测项 3】真实信号名的原生代码提取 (30分)
    # 严格杜绝正则模糊匹配，直接从 dict 的层级数据结构中寻找信号数据
    has_real_name = find_in_json(data, "axi_wdata")
    has_raw_symbol = find_in_json(data, "$")
    has_wrong_signal = find_in_json(data, "axi_wstrb")

    score_3 = 0
    reason_3 = ""
    if has_real_name and not has_raw_symbol and not has_wrong_signal:
        score_3 = 30
        reason_3 = "成功定位真实信号名 axi_wdata，且剔除了 VCD 原始 ASCII 代号，没有包含其他干扰信号"
    elif has_real_name and (has_raw_symbol or has_wrong_signal):
        score_3 = 10
        reason_3 = "包含了真实信号名，但未清洗干净（带入 VCD 代号 $ 或误抓取了干扰信号 axi_wstrb），视为不严谨"
    else:
        score_3 = 0
        reason_3 = "在 JSON 数据结构中未找到引发异常的确切真实信号名 'axi_wdata'"
        
    details.append({"item": "利用原生解析器验证真实信号名的提取纯度", "score": score_3, "max_score": 30, "passed": score_3 == 30, "reason": reason_3})
    total_score += score_3

    # 【检测项 4】时钟周期与异常注入点的时间戳判定 (30分)
    has_exact_time = find_in_json(data, "1424500")
    has_fatal_time = find_in_json(data, "1425000")
    has_z_time = find_in_json(data, "1385000")

    score_4 = 0
    reason_4 = ""
    if has_exact_time and not has_fatal_time and not has_z_time:
        score_4 = 30
        reason_4 = "成功追溯并提取了确切的异常灌入时间点 1424500 ps，完美避开后续 Fatal 点与其他高阻态跳变点"
    elif has_exact_time:
        score_4 = 15
        reason_4 = "找到了确切时间戳 1424500，但数据中存在 Fatal 时间等混淆项，未剔除干净"
    elif has_fatal_time:
        score_4 = 0
        reason_4 = "严重误判：将 UVM_FATAL 的断言时刻 1425000 当成了引发问题的原始时间点"
    elif has_z_time:
        score_4 = 0
        reason_4 = "被干扰波形误导：错误锁定了与此 Fatal 无关的高阻态跳变时间点 1385000"
    else:
        score_4 = 0
        reason_4 = "在 JSON 数据中完全没有找到正确的异常时间戳"

    details.append({"item": "验证波形逆推导致的源头异常时间戳", "score": score_4, "max_score": 30, "passed": score_4 == 30, "reason": reason_4})
    total_score += score_4

    # 【检测项 5】基于 LLM 的非结构化/语义职业素养检测 (20分)
    # 场景剧本提示"铁证直接去敲主管的门"，意味着需要极其简练，纯粹的键值对，杜绝大段无意义解释
    llm_prompt = (
        "The user provided a JSON output to act as hard evidence for a critical chip tape-out error. "
        "The instructions demanded a JSON output containing ONLY the culprit signal and its timestamp. "
        "Does the provided JSON file text contain ONLY technical data (keys and numbers), WITHOUT any redundant "
        "conversational text, verbose explanations, or excuses? "
        "(Answer 'YES' if it is purely an extremely concise technical JSON, 'NO' if it contains conversational words or verbose string explanations)."
    )
    
    is_concise = llm_judge_content(llm_prompt, content)
    if is_concise:
        details.append({"item": "大模型验证：报告是否足够干净利落，符合流片紧急事件的铁证要求", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定 JSON 极其精炼，只包含信号数据，没有多余的废话和推脱解释"})
        total_score += 20
    else:
        details.append({"item": "大模型验证：报告是否足够干净利落，符合流片紧急事件的铁证要求", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定文件中包含了冗余的解释文本或推诿语句，不够专业与精炼"})

    write_score_and_exit()

if __name__ == "__main__":
    main()
