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

def verify(workspace):
    score = 0
    details = []
    
    target_file = os.path.join(workspace, "dv_reports", "culprit_signal.json")
    
    # 1. 检查文件存在性 (10分)
    if os.path.exists(target_file):
        score += 10
        details.append({"item": "检查目标结果文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 dv_reports/culprit_signal.json 存在"})
    else:
        details.append({"item": "检查目标结果文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 dv_reports/culprit_signal.json 文件"})
        write_score(score, details)
        return

    # 2. JSON解析及字段校验 (20分)
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        has_signal = "signal" in data
        has_ts = "timestamp" in data
        
        if has_signal and has_ts:
            score += 20
            details.append({"item": "JSON格式与关键字段校验", "score": 20, "max_score": 20, "passed": True, "reason": "成功解析JSON且包含 signal 和 timestamp 核心字段"})
        else:
            details.append({"item": "JSON格式与关键字段校验", "score": 0, "max_score": 20, "passed": False, "reason": "缺少 signal 或 timestamp 核心字段"})
            write_score(score, details)
            return
            
    except Exception as e:
        details.append({"item": "JSON格式与关键字段校验", "score": 0, "max_score": 20, "passed": False, "reason": f"JSON解析失败: {e}"})
        write_score(score, details)
        return

    # 3. 结构纯净度与额外语义校验 (10分)
    extra_keys = set(data.keys()) - {"signal", "timestamp"}
    if extra_keys:
        # 如果存在多余非结构化字段，利用大模型判定是否是合法的语义补充（防幻觉策略）
        extra_content = json.dumps({k: data[k] for k in extra_keys}, ensure_ascii=False)
        prompt = (
            "The following is an extra text field submitted by an AI Agent for a chip crash debugging task. "
            "Does this content provide a reasonable and coherent explanation regarding why the simulation crashed due to 'x' or 'z' states on an AXI bus?"
        )
        is_valid_analysis = llm_judge_content(prompt, extra_content)
        
        if is_valid_analysis:
            score += 10
            details.append({"item": "检查多余字段与防幻觉", "score": 10, "max_score": 10, "passed": True, "reason": "存在额外字段，但大模型判定其包含了对崩溃原因为不定态的合理解释，不予扣分"})
        else:
            details.append({"item": "检查多余字段与防幻觉", "score": 0, "max_score": 10, "passed": False, "reason": f"发现无用或捏造的多余字段: {list(extra_keys)}，且语义无逻辑，涉嫌幻觉"})
    else:
        score += 10
        details.append({"item": "检查多余字段与防幻觉", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 结构极其纯净，无任何多余捏造字段"})

    # 4. 信号名的精准提取 (30分)
    signal_val = str(data["signal"]).strip()
    if signal_val == "axi_awready":
        score += 30
        details.append({"item": "信号末端线名的提取", "score": 30, "max_score": 30, "passed": True, "reason": "精准找到了肇事者信号，并完美切分提取了末端线名 axi_awready"})
    elif signal_val.endswith("axi_awready"):
        score += 10
        details.append({"item": "信号末端线名的提取", "score": 10, "max_score": 30, "passed": False, "reason": f"找准了肇事信号，但未遵守业务规范切分层级前缀: {signal_val}"})
    elif signal_val in ["axi_awvalid", "axi_wstrb"]:
        details.append({"item": "信号末端线名的提取", "score": 0, "max_score": 30, "passed": False, "reason": f"未能避开陷阱，错误提取了未导致崩溃的 AXI 干扰信号: {signal_val}"})
    elif "i2c" in signal_val.lower() or "sram" in signal_val.lower() or signal_val in ["i2c_sda", "sram_data"]:
        details.append({"item": "信号末端线名的提取", "score": 0, "max_score": 30, "passed": False, "reason": f"完全被非 AXI 总线的外围诱饵信号误导: {signal_val}"})
    else:
        details.append({"item": "信号末端线名的提取", "score": 0, "max_score": 30, "passed": False, "reason": f"提取出完全无关的信号标识: {signal_val}"})

    # 5. 时间戳的严格校验 (30分)
    ts_val = data["timestamp"]
    try:
        ts_val = int(ts_val)
        if ts_val == 45820500:
            score += 30
            details.append({"item": "时钟跳变点的时间定位", "score": 30, "max_score": 30, "passed": True, "reason": "在百万级跳变中，精确找出了 UVM_FATAL 爆发前的决定性时钟跳变点 (45820500)"})
        elif ts_val == 45821000:
            score += 10
            details.append({"item": "时钟跳变点的时间定位", "score": 10, "max_score": 30, "passed": False, "reason": "提取了 UVM_FATAL 的爆发时间，未向前回溯到引发崩溃的异常跳变时间点"})
        elif ts_val == 41005000:
            details.append({"item": "时钟跳变点的时间定位", "score": 0, "max_score": 30, "passed": False, "reason": "提取了过早的干扰点，未能将异常时间锚定在崩溃时刻前夕"})
        elif ts_val == 45821500:
            details.append({"item": "时钟跳变点的时间定位", "score": 0, "max_score": 30, "passed": False, "reason": "提取了崩溃之后发生的无关异常波形时间"})
        elif ts_val == 45820000:
            details.append({"item": "时钟跳变点的时间定位", "score": 0, "max_score": 30, "passed": False, "reason": "被前置一拍的非 AXI 信号跳变陷阱欺骗"})
        else:
            details.append({"item": "时钟跳变点的时间定位", "score": 0, "max_score": 30, "passed": False, "reason": f"时间点完全错误或未通过计算推导: {ts_val}"})
    except (ValueError, TypeError):
        details.append({"item": "时钟跳变点的时间定位", "score": 0, "max_score": 30, "passed": False, "reason": f"时间戳格式异常，无法转换为整型数值: {ts_val}"})

    write_score(score, details)

def write_score(score, details):
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({
            "total_score": score,
            "details": details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
