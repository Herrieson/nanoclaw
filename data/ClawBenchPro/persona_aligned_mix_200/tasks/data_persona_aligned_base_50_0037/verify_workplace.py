import os
import sys
import json
import struct
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
    # 此函数为检测非结构化文本的统一接口（本题验证以结构化原生代码判定为主，保留此防御性调用接口）
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

def parse_ground_truth(workspace):
    """
    原生验证探针核心逻辑：完全复原并解析遥测数据的 Ground Truth
    """
    log_path = os.path.join(workspace, "telemetry_dumps", "downlink_pass_critical.log")
    if not os.path.exists(log_path):
        return {}
    
    gt_data = {}
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            if "RAW_PAYLOAD:" not in line:
                continue
            # 提取 payload 部分的 hex
            hex_str = line.split("RAW_PAYLOAD:")[1].strip()
            try:
                raw_bytes = bytes.fromhex(hex_str)
            except ValueError:
                continue
            
            # 查找帧头同步字
            sync_idx = raw_bytes.find(b'\x1a\xcf\xfc\x1d')
            while sync_idx != -1:
                # 检查截断：帧头(4) + ts(4) + q(16) + crc(2) = 26 bytes
                if sync_idx + 26 <= len(raw_bytes):
                    packet = raw_bytes[sync_idx:sync_idx+26]
                    # 解析时间戳和四元数浮点（必须大端序）
                    ts = struct.unpack('>I', packet[4:8])[0]
                    q1, q2, q3, q4 = struct.unpack('>ffff', packet[8:24])
                    # 验证值合理范围
                    if all(-1.0 <= q <= 1.0 for q in (q1, q2, q3, q4)):
                        gt_data[str(ts)] = [q1, q2, q3, q4]
                        break # 一行理论上只包含一条完整有效数据
                # 寻找下一个潜在的帧头
                sync_idx = raw_bytes.find(b'\x1a\xcf\xfc\x1d', sync_idx + 1)
    return gt_data

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    # [1] 检查工作区目录和文件产生情况 (10分)
    target_dir = os.path.join(workspace, "recovery")
    target_file = os.path.join(target_dir, "attitude_quaternions.json")
    
    dir_exists = os.path.isdir(target_dir)
    file_exists = os.path.isfile(target_file)
    
    if dir_exists and file_exists:
        score_details.append({"item": "检查目标目录和文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "成功创建 recovery 目录及 attitude_quaternions.json"})
        total_score += 10
    else:
        score_details.append({"item": "检查目标目录和文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到要求的目录或文件输出"})
        
    # [2] 检查文件是否为合法 JSON (10分)
    agent_data = None
    if file_exists:
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                agent_data = json.load(f)
            score_details.append({"item": "检查 JSON 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 文件能被成功解析"})
            total_score += 10
        except Exception as e:
            score_details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
    else:
        score_details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": "依赖文件不存在，跳过检查"})
        
    # [3] 数据结构层级和类型合法性 (20分)
    format_passed = False
    if agent_data is not None:
        if isinstance(agent_data, dict):
            all_valid = True
            for k, v in agent_data.items():
                try:
                    int(k) # key必须能转为整型时间戳
                except ValueError:
                    all_valid = False
                    break
                
                if not isinstance(v, list) or len(v) != 4:
                    all_valid = False
                    break
                
                for val in v:
                    if not isinstance(val, (int, float)) or val < -1.0 or val > 1.0:
                        all_valid = False
                        break
                        
            if all_valid and len(agent_data) > 0:
                format_passed = True
                score_details.append({"item": "检查数据结构和值边界的合法性", "score": 20, "max_score": 20, "passed": True, "reason": "数据结构正确(字符串映射到4元素数组)，并且所有浮点数均在[-1.0, 1.0]边界内"})
                total_score += 20
            elif not all_valid:
                score_details.append({"item": "检查数据结构和值边界的合法性", "score": 0, "max_score": 20, "passed": False, "reason": "存在数据节点异常: 键非数字/数组长度不符/浮点数值越界"})
            else:
                score_details.append({"item": "检查数据结构和值边界的合法性", "score": 0, "max_score": 20, "passed": False, "reason": "提取出的 JSON 数据字典为空"})
        else:
            score_details.append({"item": "检查数据结构和值边界的合法性", "score": 0, "max_score": 20, "passed": False, "reason": "根节点应当是一个 JSON Object(字典)"})
    else:
        score_details.append({"item": "检查数据结构和值边界的合法性", "score": 0, "max_score": 20, "passed": False, "reason": "无可用 JSON 对象数据"})

    # [4] 精度与召回率的严格对比探针 (60分)
    if format_passed:
        gt_data = parse_ground_truth(workspace)
        if not gt_data:
            score_details.append({"item": "数据精准对比测试", "score": 0, "max_score": 60, "passed": False, "reason": "未能从沙盒环境中提取到 ground truth，验证无法继续"})
        else:
            correct_count = 0
            for k, v in agent_data.items():
                if k in gt_data:
                    gt_v = gt_data[k]
                    # 考虑到浮点数序列化的微小偏差，设置 1e-4 的容忍度
                    if all(abs(a - b) < 1e-4 for a, b in zip(v, gt_v)):
                        correct_count += 1
            
            # 使用 F1 分数来严惩产生幻觉数据或丢失数据的行为
            precision = correct_count / len(agent_data) if len(agent_data) > 0 else 0.0
            recall = correct_count / len(gt_data) if len(gt_data) > 0 else 0.0
            
            if precision + recall > 0:
                f1 = 2 * precision * recall / (precision + recall)
            else:
                f1 = 0.0
                
            data_score = int(round(f1 * 60))
            passed = (data_score == 60)
            
            score_details.append({
                "item": "数据精准对比测试 (F1-Score评估)",
                "score": data_score,
                "max_score": 60,
                "passed": passed,
                "reason": f"正确提取了 {correct_count}/{len(gt_data)} 条有效记录。Precision: {precision:.2f}, Recall: {recall:.2f}, 综合F1评定: {f1:.3f}"
            })
            total_score += data_score
    else:
        score_details.append({"item": "数据精准对比测试", "score": 0, "max_score": 60, "passed": False, "reason": "前置的数据结构和边界校验未通过，一票否决不执行对比逻辑"})

    # 输出统一规范的验证结果
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": score_details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
