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

http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
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

def get_true_quaternions():
    """复刻环境生成时的飞行轨道物理公式，拿到 30 组真值，包含struct的精度流转"""
    true_q = []
    for i in range(30):
        t = i * 0.1
        w = math.cos(t)
        x = math.sin(t) * 0.5
        y = math.sin(t) * 0.5
        z = math.sin(t) * 0.707
        norm = math.sqrt(w*w + x*x + y*y + z*z)
        # 经历一次底层装包解包，模拟精度损失
        packed = struct.pack("<ffff", w/norm, x/norm, y/norm, z/norm)
        unpacked = struct.unpack("<ffff", packed)
        true_q.append(unpacked)
    return true_q

def extract_all_numbers(obj):
    """递归提取 JSON 中的所有数值，无论它打包成什么奇怪结构"""
    nums = []
    if isinstance(obj, bool):
        pass  # 过滤布尔值以防被当作 0/1
    elif isinstance(obj, (int, float)):
        nums.append(float(obj))
    elif isinstance(obj, list):
        for item in obj:
            nums.extend(extract_all_numbers(item))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            nums.extend(extract_all_numbers(v))
    return nums

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_file = os.path.join(workspace, "flight_dynamics", "quaternions.json")
    
    total_score = 0
    details = []

    # 1. 检查目标文件存在及基础规范 (10分)
    if not os.path.exists(target_file):
        details.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到目标文件 quaternions.json"})
        return 0, details
        
    try:
        with open(target_file, "r") as f:
            raw_text = f.read()
            data = json.loads(raw_text)
        details.append({"item": "检查目标文件合法性", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在且为合法 JSON 格式"})
        total_score += 10
    except Exception as e:
        details.append({"item": "检查目标文件合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"文件不是有效的 JSON，解析错误: {e}"})
        return total_score, details

    # 获取所有提取的数值
    nums = extract_all_numbers(data)

    # 2. 规避旧协议假包陷阱 (20分)
    # 真实数据的四元数规范化后不可能是 4 个 0，如果窗口中出现了全零或极近乎零的包，一定是中招了旧文档(0x07)或提取错误。
    hit_trap = False
    for i in range(len(nums) - 3):
        window = nums[i:i+4]
        if all(abs(x) < 1e-5 for x in window):
            hit_trap = True
            break
            
    if hit_trap:
        details.append({"item": "情报陷阱规避测试", "score": 0, "max_score": 20, "passed": False, "reason": "发现提取了全零四元数，Agent 显然被旧 ICD 文档误导或协议头提取错误。"})
    elif len(nums) == 0:
        details.append({"item": "情报陷阱规避测试", "score": 0, "max_score": 20, "passed": False, "reason": "未能提取任何数字。"})
    else:
        details.append({"item": "情报陷阱规避测试", "score": 20, "max_score": 20, "passed": True, "reason": "完美规避 0x07 与 Big-Endian 的假包陷阱。"})
        total_score += 20

    # 3. 跨文件精准解码提取星象仪数据 (60分)
    expected_quaternions = get_true_quaternions()
    matched_count = 0
    search_start = 0
    
    # 采用滑动窗口防止额外附加字段（如id等）导致组对错位
    for exp_q in expected_quaternions:
        best_match_idx = -1
        for i in range(search_start, len(nums) - 3):
            ext_q = nums[i:i+4]
            # 计算绝对差的和，误差<1e-3 即视为匹配成功
            diff = sum(abs(e - a) for e, a in zip(exp_q, ext_q))
            if diff < 1e-3:
                best_match_idx = i
                break
        if best_match_idx != -1:
            matched_count += 1
            search_start = best_match_idx + 4
            
    q_score = matched_count * 2
    passed_q = (matched_count == 30)
    details.append({"item": "核心提取：跨文件断帧组装及姿态四元数恢复", "score": q_score, "max_score": 60, "passed": passed_q, "reason": f"在高度碎片化的字节流中，精准复原了 {matched_count}/30 组正确数据。"})
    total_score += q_score

    # 4. LLM 对非结构化需求("格式你定,只要能一眼看清这四个浮点数的值")做语义判卷 (10分)
    prompt = "检查这段JSON内容。要求其数据结构排版必须能让人一眼看清这是一组组包含四元数(w, x, y, z四个浮点数)的数据集，使用了有语义的 Key 或排布清晰。绝对不能是混杂乱成一团的一维单列表。是否符合良好可读性的要求？"
    trunc_text = raw_text if len(raw_text) < 2000 else raw_text[:1000] + "\n...[TRUNCATED]...\n" + raw_text[-1000:]
    is_readable = llm_judge_content(prompt, trunc_text)
    
    if is_readable and len(nums) > 0:
        details.append({"item": "结构语义化及可读性核验", "score": 10, "max_score": 10, "passed": True, "reason": "大模型判定输出结构优雅易读。"})
        total_score += 10
    else:
        details.append({"item": "结构语义化及可读性核验", "score": 0, "max_score": 10, "passed": False, "reason": "判定数据堆砌杂乱，或未能清晰呈现四元数的物理映射。"})

    return total_score, details

if __name__ == "__main__":
    score, dets = verify()
    output = {
        "total_score": score,
        "details": dets
    }
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
