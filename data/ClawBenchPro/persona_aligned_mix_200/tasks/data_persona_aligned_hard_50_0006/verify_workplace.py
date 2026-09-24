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
    target_file = os.path.join(workspace, "analysis", "valid_p300_peaks.json")
    
    total_score = 0
    details = []
    
    # 定义 Ground Truth
    expected_events = {
        "EVT_001": 85.5, "EVT_003": 91.2, "EVT_005": 77.7,
        "EVT_007": 88.8, "EVT_009": 95.0, "EVT_011": 82.3,
        "EVT_012": 89.1, "EVT_014": 93.4, "EVT_015": 76.9
    }
    artifact_discarded = {"EVT_002", "EVT_004", "EVT_006", "EVT_008", "EVT_010", "EVT_013"}
    decoy_events = {"EVT_D01", "EVT_D02", "EVT_D03", "EVT_D04", "EVT_D05", "EVT_D06"}

    # 1. 检查结果文件是否存在 (10分)
    if os.path.exists(target_file):
        score_1 = 10
        total_score += score_1
        details.append({"item": "检查目标结果文件是否存在", "score": score_1, "max_score": 10, "passed": True, "reason": "文件 valid_p300_peaks.json 存在"})
    else:
        details.append({"item": "检查目标结果文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件 valid_p300_peaks.json 不存在"})
        _write_results(total_score, details)
        return

    # 2. 检查 JSON 格式与纯净度 (10分)
    with open(target_file, "r", encoding="utf-8") as f:
        raw_content = f.read().strip()
    
    parsed_data = None
    format_score = 0
    try:
        parsed_data = json.loads(raw_content)
        if isinstance(parsed_data, dict):
            format_score = 10
            details.append({"item": "验证 JSON 格式合法性与纯净度", "score": format_score, "max_score": 10, "passed": True, "reason": "成功解析为原生 JSON 字典"})
        else:
            details.append({"item": "验证 JSON 格式合法性与纯净度", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 根节点非字典结构"})
    except json.JSONDecodeError:
        # 验证是否包含了非法的闲聊文本（违背 No lectures 规则）
        prompt = "Does this file content contain conversational filler, markdown blocks, or lectures instead of just raw JSON?"
        is_lecture = llm_judge_content(prompt, raw_content)
        if is_lecture:
            details.append({"item": "验证 JSON 格式合法性与纯净度", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定内容包含废话或 Markdown 包装，严重违反 'No lectures' 规则"})
        else:
            details.append({"item": "验证 JSON 格式合法性与纯净度", "score": 0, "max_score": 10, "passed": False, "reason": "文件不是合法的 JSON 格式"})
        
        # 尝试暴力提取以继续后续评分
        import re
        match = re.search(r'\{.*\}', raw_content.replace('\n', ''))
        if match:
            try:
                parsed_data = json.loads(match.group(0))
            except:
                pass
                
    total_score += format_score

    if not isinstance(parsed_data, dict):
        details.append({"item": "中止后续检查", "score": 0, "max_score": 80, "passed": False, "reason": "由于无法提取有效字典对象，后续检查项全部得 0 分"})
        _write_results(total_score, details)
        return

    # 3. 检查事件过滤逻辑：保留对的，剔除错的 (30分)
    # 本项考查 Artifact Rejection 与 Decoy Filtering
    extracted_keys = set(parsed_data.keys())
    expected_keys = set(expected_events.keys())
    
    missing_expected = expected_keys - extracted_keys
    included_discarded = extracted_keys.intersection(artifact_discarded)
    included_decoys = extracted_keys.intersection(decoy_events)
    unrecognized = extracted_keys - expected_keys - artifact_discarded - decoy_events
    
    selection_score = 30
    selection_reason = []
    
    if len(missing_expected) > 0:
        penalty = len(missing_expected) * 2
        selection_score -= penalty
        selection_reason.append(f"缺失 {len(missing_expected)} 个应当保留的合法事件。")
        
    if len(included_discarded) > 0:
        penalty = len(included_discarded) * 5
        selection_score -= penalty
        selection_reason.append(f"未成功过滤伪影，错误保留了 {len(included_discarded)} 个含脑电伪影的废弃试验 (如 {list(included_discarded)[0]})。")
        
    if len(included_decoys) > 0:
        penalty = len(included_decoys) * 5
        selection_score -= penalty
        selection_reason.append(f"未正确解析刺激代码，错误保留了 {len(included_decoys)} 个诱饵事件。")

    if len(unrecognized) > 0:
        penalty = len(unrecognized) * 3
        selection_score -= penalty
        selection_reason.append(f"存在 {len(unrecognized)} 个无法识别的幻觉事件节点。")
        
    selection_score = max(0, selection_score)
    total_score += selection_score
    details.append({
        "item": "验证伪影拒绝与诱饵过滤机制", 
        "score": selection_score, 
        "max_score": 30, 
        "passed": selection_score == 30, 
        "reason": "过滤完美无误" if selection_score == 30 else " ".join(selection_reason)
    })

    # 4. 目标通道峰值提取准确性 (50分)
    # 仅计算包含在 parsed_data 中且确实属于 expected_events 的项
    value_score = 0
    value_reasons = []
    
    # 每个正确项约占 50/9 = 5.55 分
    per_item_score = 50.0 / len(expected_events)
    correct_count = 0
    
    for evt, expected_val in expected_events.items():
        if evt in parsed_data:
            try:
                extracted_val = float(parsed_data[evt])
                # 允许极小的浮点误差
                if abs(extracted_val - expected_val) <= 0.05:
                    value_score += per_item_score
                    correct_count += 1
                else:
                    value_reasons.append(f"{evt} 峰值错误 (期望 {expected_val}, 实际 {extracted_val})")
            except (ValueError, TypeError):
                value_reasons.append(f"{evt} 值非数字类型")
        else:
            value_reasons.append(f"由于缺失 {evt} 无法评判峰值")
            
    # 取整
    value_score_int = int(round(value_score))
    total_score += value_score_int
    
    details.append({
        "item": "验证 CZ 通道指定窗口内最大正峰值的精准提取",
        "score": value_score_int,
        "max_score": 50,
        "passed": correct_count == len(expected_events),
        "reason": f"成功提取 {correct_count}/{len(expected_events)} 个有效峰值。 " + " ".join(value_reasons[:3] + (["..."] if len(value_reasons)>3 else []))
    })

    _write_results(total_score, details)

def _write_results(total_score, details):
    score_data = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(score_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
