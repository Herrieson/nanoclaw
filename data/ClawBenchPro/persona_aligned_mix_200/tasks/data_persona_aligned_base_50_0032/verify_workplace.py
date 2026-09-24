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

def get_ground_truth(outcar_path):
    steps_data = [] 
    current_step = None
    current_energy = None
    current_max_force = 0.0
    in_force_block = False
    
    with open(outcar_path, 'r', encoding='utf-8') as f:
        for line in f:
            # 提取 ionic step 步数
            if "Iteration" in line and "(" in line:
                parts = line.split()
                if len(parts) >= 2 and parts[0] == "Iteration":
                    s_str = parts[1].split('(')[0]
                    if s_str.isdigit():
                        s = int(s_str)
                        if current_step is not None and current_energy is not None:
                            steps_data.append({
                                'step': current_step,
                                'energy': current_energy,
                                'max_force': current_max_force
                            })
                        current_step = s
                        current_energy = None
                        current_max_force = 0.0
                        in_force_block = False
                    
            # 提取 TOTEN 能量
            if "free  energy   TOTEN" in line:
                parts = line.split('=')
                if len(parts) == 2:
                    val_str = parts[1].replace('eV', '').strip()
                    try:
                        current_energy = float(val_str)
                    except ValueError:
                        pass
                    
            # 提取 受力
            if "TOTAL-FORCE (eV/Angst)" in line:
                in_force_block = True
                continue
            
            if in_force_block:
                if "---" in line:
                    continue
                elif "timing for ionic step" in line or "BRION:" in line:
                    in_force_block = False
                else:
                    parts = line.split()
                    if len(parts) == 6:
                        try:
                            fx, fy, fz = float(parts[3]), float(parts[4]), float(parts[5])
                            max_f = max(abs(fx), abs(fy), abs(fz))
                            if max_f > current_max_force:
                                current_max_force = max_f
                        except ValueError:
                            pass
    
    # 扫尾
    if current_step is not None and current_energy is not None:
        steps_data.append({
            'step': current_step,
            'energy': current_energy,
            'max_force': current_max_force
        })
        
    # 计算滑动窗口 (5步)
    trap_step = -1
    for i in range(4, len(steps_data)):
        window = steps_data[i-4:i+1]
        energies = [x['energy'] for x in window]
        diff = max(energies) - min(energies)
        last_max_force = window[-1]['max_force']
        
        if diff < 0.05 and last_max_force > 0.05:
            trap_step = window[-1]['step']
            break
            
    if trap_step == -1:
        return None, None
        
    energies_up_to_trap = [x['energy'] for x in steps_data if x['step'] <= trap_step]
    return trap_step, energies_up_to_trap

def evaluate(workspace):
    total_score = 0
    details = []

    result_dir = os.path.join(workspace, "result")
    json_path = os.path.join(result_dir, "trap_report.json")
    outcar_path = os.path.join(workspace, "sim_data", "OUTCAR_fragment.log")

    # [1] 检查文件存在及合法性 (20分)
    file_exists = os.path.exists(json_path)
    if not file_exists:
        details.append({"item": "检查目标文件 trap_report.json 是否存在并合法", "score": 0, "max_score": 20, "passed": False, "reason": "文件不存在"})
        return 0, details
        
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            agent_data = json.load(f)
        total_score += 20
        details.append({"item": "检查目标文件 trap_report.json 是否存在并合法", "score": 20, "max_score": 20, "passed": True, "reason": "文件存在且为合法JSON"})
    except Exception as e:
        details.append({"item": "检查目标文件 trap_report.json 是否存在并合法", "score": 0, "max_score": 20, "passed": False, "reason": f"文件解析为JSON失败: {e}"})
        return total_score, details

    # [2] JSON 键名合理性检测 (10分，大模型兜底)
    keys_str = ", ".join(agent_data.keys()) if isinstance(agent_data, dict) else ""
    prompt = (
        "Are the following JSON keys intuitively clear to distinguish which key represents a single 'step number' "
        "(e.g. trap_step, trapped_iteration, step, etc.) and which key represents a sequence/list of 'energies' "
        "(e.g. energies, energy_list, sequence, etc.)? "
        "Any reasonable names that separate a singular concept and a plural/list concept are perfectly acceptable. "
        "Only answer 'NO' if they are extremely confusing, completely irrelevant, or identical."
    )
    is_keys_good = llm_judge_content(prompt, keys_str)
    if is_keys_good:
        total_score += 10
        details.append({"item": "利用大模型检查JSON键名是否具有可读性", "score": 10, "max_score": 10, "passed": True, "reason": "键名清晰易懂"})
    else:
        details.append({"item": "利用大模型检查JSON键名是否具有可读性", "score": 0, "max_score": 10, "passed": False, "reason": f"键名难以辨别: {keys_str}"})

    # [3] 从Agent的JSON提取核心内容 (5分)
    agent_step = None
    agent_energies = None
    if isinstance(agent_data, dict):
        for k, v in agent_data.items():
            if isinstance(v, (int, float)):
                agent_step = int(v)
            elif isinstance(v, str) and v.isdigit():
                agent_step = int(v)
            elif isinstance(v, list) and all(isinstance(x, (int, float)) for x in v):
                agent_energies = v

    if agent_step is not None and agent_energies is not None:
        total_score += 5
        details.append({"item": "结构解析识别成功", "score": 5, "max_score": 5, "passed": True, "reason": "成功提取出步数标量和能量数组"})
    else:
        details.append({"item": "结构解析识别成功", "score": 0, "max_score": 5, "passed": False, "reason": "无法通过类型映射出核心字段"})
        return total_score, details

    # 获取 GT
    gt_step, gt_energies = get_ground_truth(outcar_path)
    if gt_step is None:
        details.append({"item": "环境GT自检", "score": 0, "max_score": 0, "passed": False, "reason": "沙盒异常，未解析出预期卡死现象"})
        return total_score, details

    # [4] 对比卡死步数 (30分)
    if agent_step == gt_step:
        total_score += 30
        details.append({"item": "陷阱节点(卡死步数)的精确匹配", "score": 30, "max_score": 30, "passed": True, "reason": f"成功匹配真实陷阱节点: {gt_step}"})
    else:
        details.append({"item": "陷阱节点(卡死步数)的精确匹配", "score": 0, "max_score": 30, "passed": False, "reason": f"Agent提取节点为 {agent_step}, 但正确答案应为 {gt_step}"})

    # [5] 检查能量序列长度 (10分)
    if len(agent_energies) == len(gt_energies):
        total_score += 10
        details.append({"item": "检查能量序列的长度是否匹配", "score": 10, "max_score": 10, "passed": True, "reason": f"序列长度完全一致 ({len(gt_energies)} 步)"})
    else:
        details.append({"item": "检查能量序列的长度是否匹配", "score": 0, "max_score": 10, "passed": False, "reason": f"长度不匹配，Agent包含 {len(agent_energies)} 步，应为 {len(gt_energies)} 步"})
        # 长度不对后续全错直接返回
        return total_score, details

    # [6] 检查能量序列具体数值的正确性 (25分)
    error_count = 0
    for a, g in zip(agent_energies, gt_energies):
        if abs(a - g) > 1e-4:
            error_count += 1
            
    if error_count == 0:
        total_score += 25
        details.append({"item": "能量序列数值精确度校验", "score": 25, "max_score": 25, "passed": True, "reason": "所有能量数据提取均无误"})
    else:
        penalty = min(25, error_count * 5)
        earned = 25 - penalty
        total_score += earned
        details.append({"item": "能量序列数值精确度校验", "score": earned, "max_score": 25, "passed": False, "reason": f"存在 {error_count} 处数值与源文件不符（允许绝对误差 1e-4），扣除 {penalty} 分"})

    return total_score, details

if __name__ == "__main__":
    workspace_path = sys.argv[1] if len(sys.argv) > 1 else "."
    final_score, report_details = evaluate(workspace_path)
    
    result_json = {
        "total_score": final_score,
        "details": report_details
    }
    
    with open(os.path.join(workspace_path, "workplace_score.json"), 'w', encoding='utf-8') as f:
        json.dump(result_json, f, ensure_ascii=False, indent=2)
