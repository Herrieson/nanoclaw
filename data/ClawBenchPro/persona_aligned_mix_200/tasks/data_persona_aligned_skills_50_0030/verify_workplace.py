import os
import sys
import json
import httpx
from openai import OpenAI

# ==============================================================================
# 强制 API 规范初始化
# ==============================================================================
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4")

http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """大模型非结构化/复杂语义检测接口"""
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

# ==============================================================================
# 核心评测逻辑
# ==============================================================================
def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "dv_reports", "culprit_signal.json")
    
    details = []
    total_score = 0

    # 1. 检查物理文件与目录是否存在 (10分)
    if os.path.exists(report_path):
        details.append({"item": "检查目标结果文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 dv_reports/culprit_signal.json 存在"})
        total_score += 10
    else:
        details.append({"item": "检查目标结果文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 dv_reports/culprit_signal.json"})
        write_score(total_score, details)
        return # 文件不存在，直接终止后续检测

    # 2. 检查 JSON 结构合法性 (15分)
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            file_content = f.read()
            data = json.loads(file_content)
        details.append({"item": "验证 JSON 格式的合法性", "score": 15, "max_score": 15, "passed": True, "reason": "成功解析 JSON 格式"})
        total_score += 15
    except json.JSONDecodeError:
        details.append({"item": "验证 JSON 格式的合法性", "score": 0, "max_score": 15, "passed": False, "reason": "JSON 格式非法或掺杂了 Markdown/自然语言"})
        write_score(total_score, details)
        return # 格式错误，无法进行确切的值提取

    # 提取所有叶子节点的字符串和数字，以便进行确定性检索
    json_str_dump = json.dumps(data)
    flat_values = []
    if isinstance(data, dict):
        flat_values = [str(k) for k in data.keys()] + [str(v) for v in data.values()]
    elif isinstance(data, list) and len(data)>0 and isinstance(data[0], dict):
        # 兼容 [{"axi_wdata": 1424500}] 的格式
        for item in data:
            flat_values.extend([str(k) for k in item.keys()] + [str(v) for v in item.values()])
            
    # 3. 检查时间戳的精准度 (30分)
    # Fatal是1425000ps，异常跳变是1424500ps (wdata变X) 和 1385000ps (wstrb变Z)
    if "1424500" in flat_values:
        details.append({"item": "提取精确的跳变时间戳", "score": 30, "max_score": 30, "passed": True, "reason": "精准提取到最致命跳变时间: 1424500"})
        total_score += 30
    elif "1385000" in flat_values:
        details.append({"item": "提取精确的跳变时间戳", "score": 15, "max_score": 30, "passed": False, "reason": "提取到较早的异常时间(1385000)，但不是导致崩溃的直接 Fatal 前一刻"})
        total_score += 15
    else:
        details.append({"item": "提取精确的跳变时间戳", "score": 0, "max_score": 30, "passed": False, "reason": "未找到正确的时间戳，或时间提取错误"})

    # 4. 检查是否遵守“绝不要带有完整模块层级路径”的严格要求 (15分，一票否决项)
    if "top_tb.dut" in json_str_dump or "axi_interface" in json_str_dump:
        details.append({"item": "检查是否剔除完整模块层级", "score": 0, "max_score": 15, "passed": False, "reason": "违反指令：直接抄写了带层级的长路径 (top_tb.dut...)"})
    else:
        details.append({"item": "检查是否剔除完整模块层级", "score": 15, "max_score": 15, "passed": True, "reason": "成功剔除了层级信息，格式合规"})
        total_score += 15

    # 5. 检查核心罪魁祸首信号名 (15分)
    if "axi_wdata" in flat_values:
        details.append({"item": "提取正确的底层基础信号名", "score": 15, "max_score": 15, "passed": True, "reason": "精准定位到信号 axi_wdata"})
        total_score += 15
    elif "axi_wstrb" in flat_values:
        details.append({"item": "提取正确的底层基础信号名", "score": 5, "max_score": 15, "passed": False, "reason": "定位到早期的 Z 态信号 axi_wstrb，非直接致命原因"})
        total_score += 5
    else:
        details.append({"item": "提取正确的底层基础信号名", "score": 0, "max_score": 15, "passed": False, "reason": "未找到正确的异常信号名"})

    # 6. 使用 LLM 进行防幻觉与纯净度检测 (15分)
    # 目的：防止 Agent 捏造无关的信号，或者在 JSON 中编造了多余的解释性键值对（例如 "reason": "because it's X state"）
    prompt = "Review the provided JSON content. Does it ONLY contain the base signal name and the timestamp, WITHOUT any extra explanation fields, fabricated signals, conversational text, or hallucinated analysis nodes? It must be pure data mapping."
    if llm_judge_content(prompt, file_content):
        details.append({"item": "LLM 审查 JSON 数据纯净度与防幻觉", "score": 15, "max_score": 15, "passed": True, "reason": "大模型判定输出极其纯净，无编造多余字段"})
        total_score += 15
    else:
        details.append({"item": "LLM 审查 JSON 数据纯净度与防幻觉", "score": 0, "max_score": 15, "passed": False, "reason": "大模型发现数据中包含多余的解释、幻觉字段或不符合纯净键值对的要求"})

    write_score(total_score, details)

def write_score(total_score, details):
    output = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"Verify Workplace Completed. Score: {total_score}")

if __name__ == "__main__":
    main()
