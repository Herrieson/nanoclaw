import os
import sys
import json
import math
import struct
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，强制关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """
    备用的非结构化文本判别接口。
    在本任务中，主要采用原生代码进行数据验证。若后续产生自然语言报告，将依赖此方法。
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

def dump_result(score, details):
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": score, "details": details}, f, indent=2, ensure_ascii=False)

def compute_ground_truth(workspace):
    """
    利用原生代码完全复刻严谨的解析链路，算出正确的真理数据集 (Ground Truth)。
    """
    gt = {}
    base_dir = os.path.join(workspace, "telemetry_dumps")
    if not os.path.exists(base_dir):
        return gt
    
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            filepath = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            if ext not in ['.raw', '.log', '.json']:
                continue
                
            buffer_bytes = b''
            try:
                if ext == '.raw':
                    with open(filepath, 'r', encoding='utf-8') as f:
                        hex_str = f.read().replace('\n', '').replace('\r', '').replace(' ', '')
                        if len(hex_str) % 2 != 0:
                            hex_str = hex_str[:-1]
                        buffer_bytes = bytes.fromhex(hex_str)
                elif ext == '.log':
                    hex_str = ""
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for line in f:
                            if "[RX_DATA]:" in line:
                                parts = line.split("[RX_DATA]:")
                                if len(parts) > 1:
                                    hex_str += parts[1].replace(' ', '').replace('\n', '').replace('\r', '')
                    if len(hex_str) % 2 != 0:
                        hex_str = hex_str[:-1]
                    buffer_bytes = bytes.fromhex(hex_str)
                elif ext == '.json':
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        frames = data.get("telemetry", {}).get("frames", [])
                        hex_str = "".join(frames)
                        buffer_bytes = bytes.fromhex(hex_str)
            except Exception:
                continue
                
            # 搜索同步帧：1A CF FC 1D
            sync_word = b'\x1a\xcf\xfc\x1d'
            idx = 0
            while True:
                idx = buffer_bytes.find(sync_word, idx)
                if idx == -1:
                    break
                # packet 长度: 4(sync) + 4(ts) + 16(float*4) + 2(crc) = 26
                if idx + 26 <= len(buffer_bytes):
                    packet = buffer_bytes[idx:idx+26]
                    ts_bytes = packet[4:8]
                    q_bytes = packet[8:24]
                    ts = struct.unpack('>I', ts_bytes)[0]
                    
                    try:
                        q1, q2, q3, q4 = struct.unpack('>ffff', q_bytes)
                        
                        # 过滤逻辑：必须排除 NaN 及超限数值
                        def is_valid(f):
                            return not math.isnan(f) and -1.0 <= f <= 1.0
                        
                        if is_valid(q1) and is_valid(q2) and is_valid(q3) and is_valid(q4):
                            gt[str(ts)] = [q1, q2, q3, q4]
                    except Exception:
                        pass
                idx += 1
    return gt

def check_workplace(workspace):
    details = []
    total_score = 0

    # 1. 检查目标目录及文件存在性
    target_path = os.path.join(workspace, "recovery", "attitude_quaternions.json")
    if os.path.exists(target_path):
        details.append({"item": "检查目标结果文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "找到了 recovery/attitude_quaternions.json"})
        total_score += 10
    else:
        details.append({"item": "检查目标结果文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 recovery/attitude_quaternions.json，无法进行后续验证"})
        return dump_result(total_score, details)
        
    # 2. 检查 JSON 解析与基础结构
    try:
        with open(target_path, 'r', encoding='utf-8') as f:
            agent_data = json.load(f)
        if not isinstance(agent_data, dict):
            raise ValueError("Root node is not a dictionary")
        details.append({"item": "检查 JSON 格式与合法性", "score": 10, "max_score": 10, "passed": True, "reason": "文件为合法的 JSON 字典结构"})
        total_score += 10
    except Exception as e:
        details.append({"item": "检查 JSON 格式与合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败或根节点类型错误: {e}"})
        return dump_result(total_score, details)

    # 预计算 Ground Truth
    gt = compute_ground_truth(workspace)
    if not gt:
        # 特殊情况保底：如果沙盒数据被破坏，抛出测试异常
        details.append({"item": "沙盒环境完整性校验", "score": 0, "max_score": 0, "passed": False, "reason": "无法读取到任何合法的物理包，沙盒环境可能出现损坏"})
        return dump_result(total_score, details)

    # 3. Precision (精确率与毒包过滤能力): Max 40分
    precision_score = 40
    fp_count = 0
    fp_reasons = []
    
    for k, v in agent_data.items():
        if k not in gt:
            fp_count += 1
            if len(fp_reasons) < 3:
                fp_reasons.append(f"提取了不应存在的假包/毒包 (时间戳: {k})")
        else:
            gt_v = gt[k]
            if not isinstance(v, list) or len(v) != 4:
                fp_count += 1
                if len(fp_reasons) < 3:
                    fp_reasons.append(f"数据格式错误 (时间戳 {k} 对应的值必须为长度4的列表)")
                continue
            for i in range(4):
                try:
                    # 使用极其严格的小数比对，防止捏造或错误解码
                    if not math.isclose(float(v[i]), gt_v[i], rel_tol=1e-5, abs_tol=1e-5):
                        fp_count += 1
                        if len(fp_reasons) < 3:
                            fp_reasons.append(f"数值精度错误 (时间戳 {k}, 期望: {gt_v[i]}, 实际: {v[i]})")
                        break
                except Exception:
                    fp_count += 1
                    break

    deduction_p = fp_count * 4
    precision_score = max(0, precision_score - deduction_p)
    
    if precision_score == 40:
        details.append({"item": "精确提取与毒包过滤 (Precision)", "score": 40, "max_score": 40, "passed": True, "reason": "提取包全部合法有效，没有引入被污染的数据"})
    else:
        details.append({"item": "精确提取与毒包过滤 (Precision)", "score": precision_score, "max_score": 40, "passed": False, "reason": f"包含 {fp_count} 个错包或脏包。示例: {'; '.join(fp_reasons)}"})
    total_score += precision_score

    # 4. Recall (召回率与跨行拼接能力): Max 40分
    recall_score = 40
    fn_count = 0
    fn_reasons = []
    
    for k in gt.keys():
        if k not in agent_data:
            fn_count += 1
            if len(fn_reasons) < 3:
                fn_reasons.append(f"漏掉了合法的有效包 (时间戳: {k})")
                
    deduction_r = fn_count * 4
    recall_score = max(0, recall_score - deduction_r)
    
    if recall_score == 40:
        details.append({"item": "无损数据召回能力 (Recall)", "score": 40, "max_score": 40, "passed": True, "reason": "成功找到了深层目录下的所有合法真理包"})
    else:
        details.append({"item": "无损数据召回能力 (Recall)", "score": recall_score, "max_score": 40, "passed": False, "reason": f"漏掉了 {fn_count} 个合法包。可能因没有正确处理跨行截断而丢失。示例: {'; '.join(fn_reasons)}"})
    total_score += recall_score

    dump_result(total_score, details)

if __name__ == "__main__":
    workspace_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    check_workplace(workspace_dir)
