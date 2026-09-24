import os
import sys
import json
import httpx
import re
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
    
    # ---------------- 1. 由探针在环境中实时结算出绝对的 Ground Truth ----------------
    target_signal = "axi_awaddr_m7"
    target_hash = ""
    build_info_path = os.path.join(workspace, "logs", "build_info.txt")
    if os.path.exists(build_info_path):
        with open(build_info_path, "r", encoding="utf-8") as f:
            content = f.read()
            match = re.search(r"DB_HASH:\s*([a-zA-Z0-9]+)", content)
            if match:
                target_hash = match.group(1)

    target_module = ""
    deprecated_modules = []
    db_dir = os.path.join(workspace, "hw_design", "db_backups")
    if os.path.exists(db_dir):
        for fname in os.listdir(db_dir):
            if fname.endswith(".db"):
                fpath = os.path.join(db_dir, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    text = f.read()
                    # 匹配出目标信号所在的物理连线路径
                    match_mod = re.search(r"//\s*(.*?)\s*\\\\.*?" + target_signal, text)
                    if match_mod:
                        mod = match_mod.group(1).strip()
                        if f"DB_HASH: {target_hash}" in text:
                            target_module = mod
                        else:
                            deprecated_modules.append(mod)

    target_time = float('inf')
    wave_dir = os.path.join(workspace, "sim_output", "wave_dumps")
    if os.path.exists(wave_dir):
        for fname in os.listdir(wave_dir):
            if fname.endswith(".trace"):
                fpath = os.path.join(wave_dir, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    current_time = None
                    for line in f:
                        line = line.strip()
                        if line.startswith("@["):
                            time_str = line.strip("@[ ]")
                            try:
                                current_time = int(time_str)
                            except:
                                pass
                        elif target_signal in line and "X" in line:
                            # 收集乱序波形中最源头的 X 态污染时间
                            if current_time is not None and current_time < target_time:
                                target_time = current_time

    # ---------------- 2. 对 Agent 的产出实施分级侦测 ----------------
    total_score = 0
    details = []

    report_path = os.path.join(workspace, "reports", "violation_root.json")
    file_exists = os.path.exists(report_path)

    # Item 1: 基础存在性探针
    if file_exists:
        score_1 = 10
        total_score += score_1
        details.append({"item": "检查目标结果文件是否存在", "score": score_1, "max_score": 10, "passed": True, "reason": "文件 reports/violation_root.json 已生成"})
    else:
        details.append({"item": "检查目标结果文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 reports/violation_root.json 报告"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": details}, f, indent=2, ensure_ascii=False)
        return

    with open(report_path, "r", encoding="utf-8") as f:
        file_content = f.read()

    # Item 2: JSON 解析与规范探针
    is_json = False
    json_data = {}
    score_2 = 0
    try:
        json_data = json.loads(file_content)
        is_json = True
    except:
        pass

    extra_keys = set()
    if is_json:
        if isinstance(json_data, dict):
            actual_keys = set(json_data.keys())
            expected_keys = {"module_instance", "timestamp_ps"}
            if actual_keys == expected_keys:
                score_2 = 20
                details.append({"item": "检查 JSON 格式规范度", "score": score_2, "max_score": 20, "passed": True, "reason": "JSON 结构纯净，严格包含指定两项键值"})
            else:
                score_2 = 10
                extra_keys = actual_keys - expected_keys
                details.append({"item": "检查 JSON 格式规范度", "score": score_2, "max_score": 20, "passed": False, "reason": "JSON 有效但违规包含冗余/缺失字段"})
        else:
            details.append({"item": "检查 JSON 格式规范度", "score": 0, "max_score": 20, "passed": False, "reason": "JSON 载体类型并非对象(Dict)"})
    else:
        details.append({"item": "检查 JSON 格式规范度", "score": 0, "max_score": 20, "passed": False, "reason": "原生 json.loads 解析失败，文本不纯净"})

    total_score += score_2

    # Item 3: 发源时间戳数值精准度核查
    score_3 = 0
    if is_json and isinstance(json_data, dict) and "timestamp_ps" in json_data:
        val = json_data.get("timestamp_ps")
        if isinstance(val, (int, float)) and val == target_time:
            score_3 = 35
            details.append({"item": "时间戳(timestamp_ps)精准度", "score": score_3, "max_score": 35, "passed": True, "reason": "精准找出乱序碎片中的首发源时间戳"})
        elif isinstance(val, (int, float)) and val > target_time:
            score_3 = 10
            details.append({"item": "时间戳(timestamp_ps)精准度", "score": score_3, "max_score": 35, "passed": False, "reason": "提取到已被级联污染的迟到状态时间，未遍历求取最小值"})
        else:
            details.append({"item": "时间戳(timestamp_ps)精准度", "score": 0, "max_score": 35, "passed": False, "reason": f"提供的时间戳数据完全错误"})
    else:
        # LLM 宽容兜底策略 (应对格式扣分后的数值补救)
        prompt = f"The exact FIRST injected unknown state timestamp is {target_time} ps. Does the user file clearly state that the timestamp is EXACTLY {target_time}?"
        if llm_judge_content(prompt, file_content):
            score_3 = 20
            details.append({"item": "时间戳(timestamp_ps)精准度", "score": score_3, "max_score": 35, "passed": True, "reason": "【LLM兜底生效】非合法JSON但也正确传达了源头时间戳数据，予以部分分数挽回"})
        else:
            details.append({"item": "时间戳(timestamp_ps)精准度", "score": 0, "max_score": 35, "passed": False, "reason": "无法获取有效的时间戳信息"})

    total_score += score_3

    # Item 4: 硬件实例路径精准度核查
    score_4 = 0
    if is_json and isinstance(json_data, dict) and "module_instance" in json_data:
        val = json_data.get("module_instance")
        if val == target_module:
            score_4 = 35
            details.append({"item": "实例路径(module_instance)精准度", "score": score_4, "max_score": 35, "passed": True, "reason": "成功验证 DB_HASH 并提取出真实的掩膜版实例路径"})
        elif val in deprecated_modules:
            score_4 = 10
            details.append({"item": "实例路径(module_instance)精准度", "score": score_4, "max_score": 35, "passed": False, "reason": "被假象误导，使用了废弃库(deprecated)的版本，缺乏哈希对齐逻辑"})
        else:
            details.append({"item": "实例路径(module_instance)精准度", "score": 0, "max_score": 35, "passed": False, "reason": "提取的实例路径纯属臆造或抓取错误"})
    else:
        prompt = f"The exact true hardware module instance is '{target_module}'. Does the user file clearly identify this precise instance path?"
        if llm_judge_content(prompt, file_content):
            score_4 = 20
            details.append({"item": "实例路径(module_instance)精准度", "score": score_4, "max_score": 35, "passed": True, "reason": "【LLM兜底生效】非合法JSON但也识别了正确的实例路径，予以部分分数挽回"})
        else:
            details.append({"item": "实例路径(module_instance)精准度", "score": 0, "max_score": 35, "passed": False, "reason": "无法获取有效的实例路径信息"})

    total_score += score_4

    # Item 5: LLM 额外字段/作弊/幻觉严查 (惩罚项)
    if extra_keys:
        extra_info_str = json.dumps({k: json_data[k] for k in extra_keys})
        llm_prompt = "Does the following content contain fabricated physical hardware failure reasons (e.g. short circuit, voltage drop) or excessive fabricated excuses? Answer YES if it contains any hallucinated hardware reasons."
        if llm_judge_content(llm_prompt, extra_info_str):
            total_score -= 20
            details.append({"item": "大模型作弊与幻觉追查", "score": -20, "max_score": 0, "passed": False, "reason": "Agent 严重违规！在多余字段中大肆编造、幻觉了不存在的物理故障原因，启动最高额惩罚"})
        else:
            details.append({"item": "大模型作弊与幻觉追查", "score": 0, "max_score": 0, "passed": True, "reason": "多余字段虽然违规，但经大模型确认未包含底层幻觉"})

    # 汇总输出
    total_score = max(0, min(100, total_score))
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
