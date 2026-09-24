import os
import sys
import json
import math
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

def get_ground_truth():
    """复刻任务生成逻辑，获取完美的真实能量数值"""
    traj_data = []
    energy_base = -1200.0
    for step in range(1, 46):
        if step <= 20:
            energy = energy_base - (20 - (20 - step)**1.3)
        else:
            energy = energy_base - 20.0 + math.sin(step * 1.5) * 0.01
        traj_data.append(round(energy, 6))
    return traj_data

def extract_scalars(data):
    """递归提取孤立标量，防范数组混淆"""
    scalars = []
    if isinstance(data, (int, float)):
        scalars.append(data)
    elif isinstance(data, dict):
        for v in data.values():
            scalars.extend(extract_scalars(v))
    elif isinstance(data, list):
        if len(data) <= 5: # 仅对短列表内标量提取，规避主体序列引发的假阳性
            for v in data:
                scalars.extend(extract_scalars(v))
    return scalars

def find_energy_arrays(data):
    """健壮性序列查找：支持 [float] 与 [{"energy": float}, ...] 两种格式的解析"""
    candidate_arrays = []
    
    if isinstance(data, list) and len(data) == 24: # 严格要求截断到目标步数
        seq = []
        for item in data:
            if isinstance(item, (int, float)):
                seq.append(float(item))
            elif isinstance(item, dict):
                nums = [v for v in item.values() if isinstance(v, (int, float))]
                if nums:
                    # 优先选择负的绝对值较大的数值（总自由能常态）
                    selected = next((n for n in nums if n < -100), nums[0])
                    seq.append(float(selected))
        if len(seq) == 24:
            candidate_arrays.append(seq)
            
    if isinstance(data, dict):
        for v in data.values():
            candidate_arrays.extend(find_energy_arrays(v))
    elif isinstance(data, list):
        for v in data:
            candidate_arrays.extend(find_energy_arrays(v))
            
    return candidate_arrays

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_path = os.path.join(workspace, "result", "trap_report.json")
    score_file = os.path.join(workspace, "workplace_score.json")
    
    total_score = 0
    details = []

    # 1. 结构验证: 文件存在及合规性 (10分)
    if not os.path.exists(target_path):
        details.append({"item": "检查目标结果文件结构", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 result/trap_report.json 文件，判定未生成产物"})
        with open(score_file, "w", encoding="utf-8") as f:
            json.dump({"total_score": 0, "details": details}, f, ensure_ascii=False, indent=2)
        return

    try:
        with open(target_path, "r", encoding="utf-8") as f:
            result_data = json.load(f)
        details.append({"item": "检查目标结果文件结构", "score": 10, "max_score": 10, "passed": True, "reason": "目标文件存在且符合 JSON 格式"})
        total_score += 10
    except Exception as e:
        details.append({"item": "检查目标结果文件结构", "score": 0, "max_score": 10, "passed": False, "reason": f"文件不是合法的 JSON：{str(e)}"})
        with open(score_file, "w", encoding="utf-8") as f:
            json.dump({"total_score": 0, "details": details}, f, ensure_ascii=False, indent=2)
        return

    # 2. 定位验证: 是否计算并找出了精确的局部陷阱步数 24 (30分)
    scalars = extract_scalars(result_data)
    has_target_step = any(abs(s - 24) < 1e-5 for s in scalars)
    
    if has_target_step:
        details.append({"item": "成功定位精确的局部陷阱步数", "score": 30, "max_score": 30, "passed": True, "reason": "成功找到了通过滑动窗口计算得出的第 24 步"})
        total_score += 30
    else:
        details.append({"item": "成功定位精确的局部陷阱步数", "score": 0, "max_score": 30, "passed": False, "reason": f"提取到的标量 {scalars} 中未包含正确步数 24，滑窗逻辑推导失败或发生幻觉"})

    # 3. 截断控制: 检查能量数组长度是否精准等于截断步数 24 (30分)
    candidate_arrays = find_energy_arrays(result_data)
    if candidate_arrays:
        details.append({"item": "成功提取能量序列(长度合法性检查)", "score": 30, "max_score": 30, "passed": True, "reason": "成功提取了长度为 24 的连续能量记录，严格满足了打包至当前步骤的要求"})
        total_score += 30
    else:
        details.append({"item": "成功提取能量序列(长度合法性检查)", "score": 0, "max_score": 30, "passed": False, "reason": "未找到长度为 24 的能量序列数组，未从第一步提取到卡死步或者未以数组形式储存"})

    # 4. 精准度核验: 抽样对比首尾与中间部分，严防 LLM 数据捏造/幻觉 (30分)
    gt_energies = get_ground_truth()[:24]
    precision_passed = False
    
    if candidate_arrays:
        for arr in candidate_arrays:
            is_match = True
            # 核验核心控制点：起点，窗口中间，尾部边缘
            for idx in [0, 5, 10, -1]:
                if abs(arr[idx] - gt_energies[idx]) > 0.05:
                    is_match = False
                    break
            if is_match:
                precision_passed = True
                break
                
    if precision_passed:
        details.append({"item": "能量序列数值真实精准度验证", "score": 30, "max_score": 30, "passed": True, "reason": "提取出的多采样点能量数值与真实模拟结果误差<0.05，数据完全真实准确，未发生幻觉作弊"})
        total_score += 30
    else:
        score_val = 0
        if candidate_arrays:
            reason_str = "提取了正确长度的数组，但核验发现核心数值发生篡改或严重误差，判定为数据捏造"
        else:
            reason_str = "由于前置缺失正确序列，故数值核验为 0 分"
        details.append({"item": "能量序列数值真实精准度验证", "score": score_val, "max_score": 30, "passed": False, "reason": reason_str})

    # 输出综合计分板
    with open(score_file, "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": details
        }, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
