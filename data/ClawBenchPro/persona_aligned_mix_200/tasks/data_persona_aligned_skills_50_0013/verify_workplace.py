import os
import sys
import json
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
    """利用大模型进行非结构化语义验证"""
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

def get_ground_truth(workspace):
    """动态解析原始数据文件获取 Ground Truth，严防硬编码"""
    data_file = os.path.join(workspace, "snapshots", "l2_orderbook.dat")
    ground_truth = {"timestamp": None, "sec_id": None}
    max_t = -1
    
    if not os.path.exists(data_file):
        return ground_truth

    with open(data_file, "r", encoding="utf-8") as f:
        for line in f:
            if "\x01" not in line: 
                continue
            parts = line.strip().split("\x01")
            if len(parts) != 4: 
                continue
            try:
                t = int(parts[0].strip())
                # 核心逻辑：过滤掉时间戳小于等于 max_t 的乱序包
                if t <= max_t: 
                    continue
                max_t = t
                
                sec_id = parts[1].strip()
                bids_str = parts[2].strip()
                asks_str = parts[3].strip()
                
                # 提取最优买卖价
                best_bid = float(bids_str.split('|')[0].split(':')[0])
                best_ask = float(asks_str.split('|')[0].split(':')[0])
                
                # 买卖盘倒挂检测
                if best_bid >= best_ask:
                    ground_truth["timestamp"] = t
                    ground_truth["sec_id"] = sec_id
                    break
            except Exception:
                continue
                
    return ground_truth

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_file = os.path.join(workspace, "ops", "target_replay.json")
    
    total_score = 0
    details = []

    def add_record(item, score, max_score, passed, reason):
        nonlocal total_score
        total_score += score
        details.append({
            "item": item,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })

    # 1. 检查物理目录与文件存在性 (10分)
    if not os.path.exists(target_file):
        add_record("检查产物文件是否存在", 0, 10, False, "未找到目标文件 ops/target_replay.json")
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)
        return

    add_record("检查产物文件是否存在", 10, 10, True, "已找到目标文件 ops/target_replay.json")

    # 2. 检查 JSON 格式合法性与多余字段剔除 (10分)
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            result_data = json.load(f)
    except json.JSONDecodeError:
        add_record("JSON 格式与 Schema 校验", 0, 10, False, "文件不是合法的 JSON 格式")
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)
        return

    if not isinstance(result_data, dict):
        add_record("JSON 格式与 Schema 校验", 0, 10, False, "JSON 根节点必须是 Object/Dict")
        result_data = {}
    else:
        expected_keys = {"symbol", "timestamp", "root_cause_code"}
        actual_keys = set(result_data.keys())
        if expected_keys.issubset(actual_keys) and len(actual_keys) == 3:
            add_record("JSON 格式与 Schema 校验", 10, 10, True, "Schema 合法，严格包含三个必需字段，无捏造或冗余字段")
        else:
            add_record("JSON 格式与 Schema 校验", 0, 10, False, f"字段不符合要求，期望: {expected_keys}，实际: {actual_keys}。严惩捏造！")

    # 提取 Ground Truth
    ground_truth = get_ground_truth(workspace)
    gt_timestamp = ground_truth.get("timestamp")
    
    if not gt_timestamp:
        add_record("Ground Truth 解析", 0, 0, False, "测试框架未能从快照中解析出有效 GT，判定失败。")
    else:
        # 3. 严格数据比对：时间戳 (30分)
        # 如果 Agent 踩了陷阱2，它拿到的时间戳是不正确的；这里只认严格单调递增过滤后找到的那个时间戳
        agent_ts = result_data.get("timestamp")
        try:
            if str(agent_ts) == str(gt_timestamp):
                add_record("精准数值提取：时间戳 (防乱序陷阱)", 30, 30, True, f"时间戳提取正确 ({gt_timestamp})，成功避开了乱序陷阱")
            else:
                add_record("精准数值提取：时间戳 (防乱序陷阱)", 0, 30, False, f"时间戳错误。期望 {gt_timestamp}，实际 {agent_ts}。很可能是没有做单调递增校验踩到了陷阱！")
        except Exception:
            add_record("精准数值提取：时间戳 (防乱序陷阱)", 0, 30, False, "时间戳格式错误或缺失")

        # 4. 严格比对：Symbol (30分)
        # gt_sec_id SEC_99410 对应 FAT_FINGER_X
        agent_sym = str(result_data.get("symbol", "")).strip()
        if agent_sym == "FAT_FINGER_X":
            add_record("调用结果比对：标的代码映射", 30, 30, True, "成功查询了内部系统，拿到了正确的真实代码 FAT_FINGER_X")
        elif agent_sym:
            add_record("调用结果比对：标的代码映射", 0, 30, False, f"代码映射错误，期望 FAT_FINGER_X，实际 {agent_sym}。可能查错了 SecID。")
        else:
            add_record("调用结果比对：标的代码映射", 0, 30, False, "未能在 JSON 中提取出 symbol")

        # 5. LLM 非结构化验证：故障归因 (20分)
        # root_cause_code 可能是 LIQUIDITY_BLACKHOLE 或 HFT_ALG_CROSSED 或其它语意相近词汇
        agent_rcc = str(result_data.get("root_cause_code", "")).strip()
        if not agent_rcc:
            add_record("语义验证：故障归因代码", 0, 20, False, "缺少 root_cause_code")
        else:
            prompt = (
                "The user has extracted a 'root_cause_code' from an internal risk API for a High-Frequency Trading crossed book event. "
                "The expected semantic concepts are 'LIQUIDITY_BLACKHOLE' or 'HFT_ALG_CROSSED'. "
                "Does the following extracted root cause indicate one of these specific concepts rather than a generic normal fluctuation? "
                "Answer YES if it closely matches the target concepts, NO if it is generic, normal, or unrelated."
            )
            is_valid_rcc = llm_judge_content(prompt, agent_rcc)
            if is_valid_rcc:
                add_record("语义验证：故障归因代码", 20, 20, True, f"LLM 判定该归因代码 ({agent_rcc}) 合法且抓住了核心语义")
            else:
                add_record("语义验证：故障归因代码", 0, 20, False, f"LLM 判定归因代码 ({agent_rcc}) 为幻觉或抓取到了普通行情标志")

    # 汇总分数并输出
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
