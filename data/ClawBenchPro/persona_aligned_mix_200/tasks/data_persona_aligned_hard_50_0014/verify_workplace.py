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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1. 检查结果目录和目标文件是否存在 (10分)
    report_path = os.path.join(workspace, "report", "root_cause.json")
    if os.path.exists(report_path):
        score += 10
        details.append({"item": "检查目标文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "成功创建了 report/root_cause.json 目标文件"})
    else:
        details.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 report/root_cause.json"})

    # 2. 确定性解析与严格内容检查 (80分)
    if os.path.exists(report_path):
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 2.1 检查 Schema 和数据类型 (20分)
            expected_keys = {"device_address", "register_address", "illegal_value"}
            actual_keys = set(data.keys())
            if actual_keys == expected_keys and all(isinstance(data.get(k), str) for k in expected_keys):
                score += 20
                details.append({"item": "检查 JSON Schema 规范性", "score": 20, "max_score": 20, "passed": True, "reason": "严格遵守了指定的3个key，且所有 value 均为字符串。"})
            else:
                details.append({"item": "检查 JSON Schema 规范性", "score": 0, "max_score": 20, "passed": False, "reason": f"存在多余/缺失的key，或数据类型不是纯字符串。当前 keys: {actual_keys}"})

            # 2.2 检查 device_address (20分)
            dev_addr = str(data.get("device_address", "")).strip().lower()
            if dev_addr == "0x5c":
                score += 20
                details.append({"item": "检查设备地址 (device_address)", "score": 20, "max_score": 20, "passed": True, "reason": "正确追踪多级文档推导出 0x5C 地址。"})
            else:
                details.append({"item": "检查设备地址 (device_address)", "score": 0, "max_score": 20, "passed": False, "reason": f"错误的设备地址: {dev_addr}。预期: 0x5c。可能未考虑到 Rev B 的 Pin strapped 状态。"})

            # 2.3 检查 register_address (20分)
            reg_addr = str(data.get("register_address", "")).strip().lower()
            if reg_addr == "0x10":
                score += 20
                details.append({"item": "检查寄存器地址 (register_address)", "score": 20, "max_score": 20, "passed": True, "reason": "正确排除干扰找准目标 OVP 寄存器 0x10。"})
            else:
                details.append({"item": "检查寄存器地址 (register_address)", "score": 0, "max_score": 20, "passed": False, "reason": f"错误的寄存器地址: {reg_addr}。预期: 0x10。"})

            # 2.4 检查 illegal_value (20分)
            ill_val = str(data.get("illegal_value", "")).strip().lower()
            if ill_val == "0x4b":
                score += 20
                details.append({"item": "检查越界写入值 (illegal_value)", "score": 20, "max_score": 20, "passed": True, "reason": "正确扫描日志碎片，精确定位触发崩溃的 0x4B 写入！"})
            else:
                details.append({"item": "检查越界写入值 (illegal_value)", "score": 0, "max_score": 20, "passed": False, "reason": f"错误的越界写入值: {ill_val}。预期: 0x4b。可能被 GLITCH 行或不相干数值干扰。"})

        except json.JSONDecodeError:
            details.append({"item": "解析目标 JSON", "score": 0, "max_score": 80, "passed": False, "reason": "目标 JSON 文件格式损坏，无法作为结构化数据解析！严重失误！"})
        except Exception as e:
            details.append({"item": "解析目标 JSON", "score": 0, "max_score": 80, "passed": False, "reason": f"读取或解析过程中发生异常: {e}"})
    else:
        details.append({"item": "确定性内容校验", "score": 0, "max_score": 80, "passed": False, "reason": "因为 root_cause.json 缺失，此部分不予评分。"})

    # 3. LLM 语义检测：检查是否残留了符合要求的非结构化分析脚本 (10分)
    # 不依赖猜测，而是寻找 Agent 遗留在工作区的 .py/.sh 文件，确认它是真正的读取+异常处理脚本，而不是 hardcode 欺骗。
    script_files = []
    for root, dirs, files in os.walk(workspace):
        if ".git" in root or "__pycache__" in root:
            continue
        for file in files:
            if file.endswith((".py", ".sh")) and file not in ["env_builder.py", "verify_workplace.py"]:
                script_files.append(os.path.join(root, file))

    if script_files:
        script_contents = ""
        for pf in script_files[:3]: # 取前3个样本防止超长
            try:
                with open(pf, "r", encoding="utf-8") as f:
                    script_contents += f"\n--- {os.path.basename(pf)} ---\n{f.read()[:3000]}"
            except:
                pass

        if script_contents.strip():
            prompt_text = "Does the following script contain logical code to batch process multiple log files (e.g. loops/glob), parse text lines to extract protocol payloads, and include some form of robust handling (e.g. regex matching, try-except, ignoring noise/glitches) instead of just hardcoding final answers?"
            is_robust_script = llm_judge_content(prompt_text, script_contents)
            
            if is_robust_script:
                score += 10
                details.append({"item": "大模型语义分析: 探查工具链合理性", "score": 10, "max_score": 10, "passed": True, "reason": "LLM 确认 Agent 在工作区遗留的脚本具备真实的批处理和容错分析语义。"})
            else:
                details.append({"item": "大模型语义分析: 探查工具链合理性", "score": 0, "max_score": 10, "passed": False, "reason": "LLM 判定遗留的脚本缺乏批处理容错逻辑，有穷举或幻觉硬猜嫌疑。"})
        else:
             details.append({"item": "大模型语义分析: 探查工具链合理性", "score": 0, "max_score": 10, "passed": False, "reason": "找到的脚本内容为空。"})
    else:
         details.append({"item": "大模型语义分析: 探查工具链合理性", "score": 0, "max_score": 10, "passed": False, "reason": "工作区未发现 Agent 编写的自定义批处理分析脚本(Agent未听从 Write a script if you have to 的建议或未保存代码)。"})

    # 输出结果报告
    result = {
        "total_score": score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    verify()
