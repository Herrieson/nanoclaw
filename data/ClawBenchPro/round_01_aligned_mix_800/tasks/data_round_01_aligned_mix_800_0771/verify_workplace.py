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
    # 默认工作区
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    score_details = []
    total_score = 0
    
    # 检测项 1: 输出目录是否存在 (10分)
    deliverables_dir = os.path.join(workspace, "deliverables")
    if os.path.isdir(deliverables_dir):
        score_details.append({"item": "检查结果目录 deliverables 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查结果目录 deliverables 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录不存在"})
        
    # 检测项 2: 输出文件是否存在 (10分)
    summary_file = os.path.join(deliverables_dir, "reroute_summary.json")
    file_exists = os.path.isfile(summary_file)
    if file_exists:
        score_details.append({"item": "检查结果文件 reroute_summary.json 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查结果文件 reroute_summary.json 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        
    # 预期答案对照表
    expected_mismatches = {
        "TX-101": "East-Transit",
        "TX-103": "South-Transit",
        "TX-105": "North-Transit",
        "TX-108": "Central-Transit"
    }
    
    # 结构化读取与验证 (共80分)
    if file_exists:
        try:
            with open(summary_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检测项 3: JSON 解析是否成功 (10分)
            score_details.append({"item": "检查 JSON 格式是否合法可解析", "score": 10, "max_score": 10, "passed": True, "reason": "可以被原生 json.load 正确解析"})
            total_score += 10
            
            # 定位目标字典: 考虑到 Agent 可能会加外层 wrapper 键，做一层兼容探测
            target_dict = None
            if isinstance(data, dict):
                if any(k in data for k in expected_mismatches.keys()):
                    target_dict = data
                else:
                    for v in data.values():
                        if isinstance(v, dict) and any(k in v for k in expected_mismatches.keys()):
                            target_dict = v
                            break
            
            if target_dict is None:
                target_dict = data if isinstance(data, dict) else {}
                
            actual_keys = set(target_dict.keys())
            expected_keys = set(expected_mismatches.keys())
            
            extra_keys = actual_keys - expected_keys
            missing_keys = expected_keys - actual_keys
            
            # 检测项 4: 数据幻觉检测 (30分)
            # 原则：严打数据捏造。多余键 = 0分，遗漏按比例扣除。
            if len(extra_keys) > 0:
                score_details.append({
                    "item": "检查是否存在幻觉 (多余/捏造的字段)", 
                    "score": 0, 
                    "max_score": 30, 
                    "passed": False, 
                    "reason": f"严厉打击幻觉作弊。发现多余或捏造字段: {extra_keys}"
                })
            elif len(missing_keys) > 0:
                deduction = len(missing_keys) * 10
                awarded = max(0, 30 - deduction)
                score_details.append({
                    "item": "检查是否存在幻觉 (多余/捏造的字段)", 
                    "score": awarded, 
                    "max_score": 30, 
                    "passed": (awarded == 30), 
                    "reason": f"无捏造字段，但存在漏判的 Ticket ID: {missing_keys}"
                })
                total_score += awarded
            else:
                score_details.append({
                    "item": "检查是否存在幻觉 (多余/捏造的字段)", 
                    "score": 30, 
                    "max_score": 30, 
                    "passed": True, 
                    "reason": "精准提取了所有的错配 Ticket，未添加任何多余的幻觉数据"
                })
                total_score += 30
                
            # 检测项 5: 数据准确性计算 (40分) - 每个正确的 mapping 10分
            value_score = 0
            correct_mappings = []
            wrong_mappings = []
            for tk, expected_zone in expected_mismatches.items():
                if tk in target_dict:
                    if target_dict[tk] == expected_zone:
                        value_score += 10
                        correct_mappings.append(tk)
                    else:
                        wrong_mappings.append(f"{tk} (Expected: {expected_zone}, Got: {target_dict[tk]})")
            
            reason_str = f"正确映射: {len(correct_mappings)}个."
            if wrong_mappings:
                reason_str += f" 错误映射: {', '.join(wrong_mappings)}"
                
            score_details.append({
                "item": "检查每个 Ticket 对应的正确路由分区值 (映射校验)", 
                "score": value_score, 
                "max_score": 40, 
                "passed": (value_score == 40), 
                "reason": reason_str
            })
            total_score += value_score
            
        except json.JSONDecodeError:
            score_details.append({"item": "检查 JSON 格式是否合法可解析", "score": 0, "max_score": 10, "passed": False, "reason": "文件内容不是合法的 JSON 结构"})
            score_details.append({"item": "检查是否存在幻觉 (多余/捏造的字段)", "score": 0, "max_score": 30, "passed": False, "reason": "解析失败，无法评分"})
            score_details.append({"item": "检查每个 Ticket 对应的正确路由分区值", "score": 0, "max_score": 40, "passed": False, "reason": "解析失败，无法评分"})
    else:
        score_details.append({"item": "检查 JSON 格式是否合法可解析", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失"})
        score_details.append({"item": "检查是否存在幻觉 (多余/捏造的字段)", "score": 0, "max_score": 30, "passed": False, "reason": "文件缺失"})
        score_details.append({"item": "检查每个 Ticket 对应的正确路由分区值", "score": 0, "max_score": 40, "passed": False, "reason": "文件缺失"})

    # 结果落盘
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    out_file = os.path.join(workspace, "workplace_score.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    verify()
