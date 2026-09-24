import os
import sys
import json
import csv
import re
import math
import httpx
from openai import OpenAI

# ---------------------------------------------------------
# [1] LLM API 配置 (强制规范，用于非结构化语义分析，按需调用)
# ---------------------------------------------------------
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
    """大模型判定接口：严格输出 YES 或 NO"""
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

# ---------------------------------------------------------
# [2] 动态计算 Ground Truth (解耦所有魔法数值，100%确定性)
# ---------------------------------------------------------
def calculate_ground_truth(workspace):
    """
    通过 Python 原生代码遍历并精确计算目标目录的期望结果，
    无视随机生成的数量和数值干扰，确立唯一真实解。
    """
    mat_dict_path = os.path.join(workspace, "mill_data", "codes", "material_dictionary.json")
    if not os.path.exists(mat_dict_path):
        return None
        
    with open(mat_dict_path, 'r') as f:
        mat_dict = json.load(f)
    
    target_code = None
    for k, v in mat_dict.items():
        if v == "White Oak":
            target_code = k
            break
            
    if not target_code:
        return None

    expected_boards = {}
    logs_dir = os.path.join(workspace, "mill_data", "inventory_logs")
    
    if not os.path.exists(logs_dir):
        return None
        
    # 严格遍历合法目录，拒绝 archive
    for root, dirs, files in os.walk(logs_dir):
        for file in files:
            path = os.path.join(root, file)
            # 根据后缀严格解析
            if file.endswith('.csv'):
                with open(path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row.get('Condition') == 'Usable' and row.get('Material_Code') == target_code:
                            t = float(row['Thickness_in'])
                            w = float(row['Width_in'])
                            l = float(row['Length_in'])
                            expected_boards[row['Item_ID']] = (t * w * l) / 144.0
                            
            elif file.endswith('.json'):
                with open(path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        for item in data:
                            if item.get('status') == 'Usable' and item.get('mat') == target_code:
                                dims = item['dims_inches'].split('x')
                                t, w, l = float(dims[0]), float(dims[1]), float(dims[2])
                                expected_boards[item['ref_id']] = (t * w * l) / 144.0
                    except:
                        pass
                        
            elif file.endswith('.log'):
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if "[RECORD]" in line:
                            # 格式化参考: [RECORD] ID:ITEM-xxx | MatCode:WO-01 | Size(in):2x12x96 | State:Usable
                            match = re.search(r"ID:(\S+)\s+\|\s+MatCode:(\S+)\s+\|\s+Size\(in\):([\d\.]+)x([\d\.]+)x([\d\.]+)\s+\|\s+State:(\S+)", line)
                            if match:
                                i_id, mat, t, w, l, cond = match.groups()
                                if cond.strip() == 'Usable' and mat.strip() == target_code:
                                    expected_boards[i_id] = (float(t) * float(w) * float(l)) / 144.0
    
    expected_total = sum(expected_boards.values())
    return expected_total, expected_boards

# ---------------------------------------------------------
# [3] 核心测评逻辑 (多梯度维度打分机制)
# ---------------------------------------------------------
def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    total_score = 0
    details = []
    
    report_path = os.path.join(workspace, "project_planning", "usable_oak_report.json")
    
    # 维度1: 文件系统与存在性 [10 points]
    if os.path.exists(report_path):
        total_score += 10
        details.append({"item": "检查目标结果文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": f"成功在正确路径生成了 usable_oak_report.json"})
    else:
        details.append({"item": "检查目标结果文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到输出文件，缺失 project_planning/usable_oak_report.json"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=4)
        return
        
    # 维度2: 结构化解析与 Schema 合法性 [10 points]
    try:
        with open(report_path, "r", encoding='utf-8') as f:
            agent_data = json.load(f)
        total_score += 10
        details.append({"item": "检查 JSON 解析合法性", "score": 10, "max_score": 10, "passed": True, "reason": "文件符合标准 JSON 规范，无语法错误"})
    except Exception as e:
        details.append({"item": "检查 JSON 解析合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"文件并非有效 JSON: {e}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=4)
        return

    # 维度3: 业务字段完整度 [20 points]
    struct_score = 0
    reason_struct = []
    
    if "total_board_feet" in agent_data and isinstance(agent_data["total_board_feet"], (int, float)):
        struct_score += 10
        reason_struct.append("包含合法数值型 total_board_feet 字段")
    else:
        reason_struct.append("缺失 total_board_feet 字段或类型不符")
        
    if "boards" in agent_data and isinstance(agent_data["boards"], list):
        if len(agent_data["boards"]) > 0:
            first_item = agent_data["boards"][0]
            if isinstance(first_item, dict) and "id" in first_item and "board_feet" in first_item:
                struct_score += 10
                reason_struct.append("包含合法的 boards 数组并携带要求的子键")
            else:
                reason_struct.append("boards 数组内容对象缺失 id 或 board_feet 子键")
        else:
            struct_score += 10
            reason_struct.append("boards 为空数组，格式判定通过")
    else:
        reason_struct.append("缺失 boards 数组结构")
        
    total_score += struct_score
    details.append({"item": "检查报告内容字段结构", "score": struct_score, "max_score": 20, "passed": struct_score == 20, "reason": "; ".join(reason_struct)})

    if struct_score < 20 and ("boards" not in agent_data or not isinstance(agent_data["boards"], list)):
        # 如果连基本的数组结构都没有，停止后续计算比对
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=4)
        return

    # 获取绝对正确的参照数值
    gt_res = calculate_ground_truth(workspace)
    if gt_res:
        expected_total, expected_boards = gt_res
        
        # 维度4: 幻觉、陷阱与噪音规避检查 [20 points]
        has_trap = False
        has_bak_tmp = False
        for b in agent_data["boards"]:
            bid = str(b.get("id", ""))
            # TRAP 系列来自 archive 陷阱夹
            if "TRAP" in bid or "archive" in bid.lower():
                has_trap = True
            # ITEM-99999 是故意放在 .bak 和 .tmp 中的坏数据
            if "ITEM-99999" in bid:
                has_bak_tmp = True
                
        trap_score = 20
        trap_reason = "成功规避了 archive 归档陷阱目录，并忽略了非日志后缀文件(.tmp/.bak)"
        if has_trap or has_bak_tmp:
            trap_score = 0
            trap_reason = "严重幻觉/脏读扣分：Agent 读取了不应读取的 archive 目录或备份文件的脏数据！"
            
        total_score += trap_score
        details.append({"item": "陷阱扫描与幻觉规避", "score": trap_score, "max_score": 20, "passed": trap_score == 20, "reason": trap_reason})

        # 维度5: 总数值宏观精度比对 [20 points]
        agent_total = float(agent_data.get("total_board_feet", 0))
        if math.isclose(agent_total, expected_total, rel_tol=1e-3, abs_tol=0.1):
            total_score += 20
            details.append({"item": "校验 total_board_feet 计算正确性", "score": 20, "max_score": 20, "passed": True, "reason": f"总木板英尺量核对无误。预期: {expected_total:.3f}, 提交: {agent_total:.3f}"})
        else:
            details.append({"item": "校验 total_board_feet 计算正确性", "score": 0, "max_score": 20, "passed": False, "reason": f"总木板英尺量出现偏差。预期: {expected_total:.3f}, 提交: {agent_total:.3f}"})

        # 维度6: 微观单木材个体映射精度比对 [20 points]
        agent_boards_dict = {str(b.get("id")): float(b.get("board_feet", 0)) for b in agent_data["boards"]}
        expected_ids_set = set(expected_boards.keys())
        agent_ids_set = set(agent_boards_dict.keys())
        
        missing = expected_ids_set - agent_ids_set
        extra = agent_ids_set - expected_ids_set
        
        if len(missing) == 0 and len(extra) == 0:
            val_error = False
            for k, v in expected_boards.items():
                if not math.isclose(v, agent_boards_dict[k], rel_tol=1e-3, abs_tol=0.01):
                    val_error = True
                    break
            if not val_error:
                total_score += 20
                details.append({"item": "校验单体木材明细提取与计算", "score": 20, "max_score": 20, "passed": True, "reason": "精准提取了所有有效木料 ID 及其对于的体积，无任何多余或遗漏。"})
            else:
                total_score += 10
                details.append({"item": "校验单体木材明细提取与计算", "score": 10, "max_score": 20, "passed": False, "reason": "成功锁定了所有正确 ID，但部分木板个体的计算精度/公式出现微小偏差。"})
        else:
            reason_str = f"木材数据抽取不准。遗漏合法记录: {len(missing)}条，多出非法记录: {len(extra)}条。"
            
            # 引入 Recall 给部分分的梯度策略
            if len(expected_ids_set) > 0:
                intersect = expected_ids_set.intersection(agent_ids_set)
                recall_ratio = len(intersect) / len(expected_ids_set)
                p_score = int(10 * recall_ratio)
            else:
                p_score = 0
                
            # 若掉入陷阱，微观匹配不再给予部分同情分
            if trap_score == 0: 
                p_score = 0 
                
            total_score += p_score
            details.append({"item": "校验单体木材明细提取与计算", "score": p_score, "max_score": 20, "passed": False, "reason": reason_str})

    # 输出结果报告
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
