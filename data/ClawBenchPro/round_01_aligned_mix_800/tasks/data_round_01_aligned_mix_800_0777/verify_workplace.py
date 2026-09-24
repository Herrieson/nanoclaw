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

def match_uninvited(data, target_set):
    """递归遍历结构化数据，寻找与目标集合完全一致的列表"""
    if isinstance(data, list):
        # 尝试将当前列表转为集合比对
        try:
            if set(data) == target_set:
                return True
        except TypeError:
            pass # 包含不可哈希类型则跳过
        # 递归检查列表元素
        return any(match_uninvited(i, target_set) for i in data)
    elif isinstance(data, dict):
        return any(match_uninvited(v, target_set) for v in data.values())
    return False

def match_tally(data, target_dict):
    """递归遍历结构化数据，寻找与目标字典完全一致的字典结构"""
    if isinstance(data, dict):
        # 精准匹配目标字典
        if data == target_dict:
            return True
        # 递归检查子节点
        return any(match_tally(v, target_dict) for v in data.values())
    elif isinstance(data, list):
        # 兼容一种常见的错误格式：列表包字典 [{"cuisine": "American", "count": 2}, ...]
        try:
            converted = {}
            for item in data:
                if isinstance(item, dict) and len(item) == 2:
                    k = [v for v in item.values() if isinstance(v, str)][0]
                    v = [v for v in item.values() if isinstance(v, int) or (isinstance(v, str) and v.isdigit())][0]
                    converted[k] = int(v)
            if converted == target_dict:
                return True
        except Exception:
            pass
        return any(match_tally(i, target_dict) for i in data)
    return False

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    score_details = []
    total_score = 0
    
    deliverables_dir = os.path.join(workspace, "deliverables")
    report_path = os.path.join(deliverables_dir, "festival_report.json")
    
    # Check 1: 目录与文件结构 (10 pts)
    if os.path.isdir(deliverables_dir) and os.path.isfile(report_path):
        score_details.append({"item": "检查结果目录与文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 deliverables/festival_report.json 存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查结果目录与文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 deliverables/festival_report.json"})
        
        # 核心文件缺失，后续检查无意义，直接输出
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # Check 2: JSON 解析与 Schema 合法性 (20 pts)
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        score_details.append({"item": "检查 JSON 格式合法性", "score": 20, "max_score": 20, "passed": True, "reason": "JSON 文件可以成功解析"})
        total_score += 20
    except json.JSONDecodeError:
        score_details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 20, "passed": False, "reason": "JSON 格式损坏，无法解析"})
        
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # Check 3: 提取未授权车辆名单 (30 pts)
    # 根据构建脚本环境，未在 CSV 中的车辆应为 "ID-SN34K", "MT-N0N0", "WY-B4D1"
    target_uninvited = {"ID-SN34K", "MT-N0N0", "WY-B4D1"}
    if match_uninvited(json_data, target_uninvited):
        score_details.append({"item": "验证未授权车辆名单", "score": 30, "max_score": 30, "passed": True, "reason": "精确提取到了所有非授权名单（ID-SN34K, MT-N0N0, WY-B4D1）且无多余捏造项"})
        total_score += 30
    else:
        score_details.append({"item": "验证未授权车辆名单", "score": 0, "max_score": 30, "passed": False, "reason": "未能精准提取未授权车辆列表，或包含多余的幻觉数据。严格禁止模糊匹配。"})

    # Check 4: 统计授权供应商菜系 (30 pts)
    target_tally = {"American": 2, "Thai": 2, "Native American": 2, "Italian": 2, "Korean": 1}
    if match_tally(json_data, target_tally):
        score_details.append({"item": "验证菜系统计结果", "score": 30, "max_score": 30, "passed": True, "reason": "结构化解析出完美的菜系数量统计结果"})
        total_score += 30
    else:
        score_details.append({"item": "验证菜系统计结果", "score": 0, "max_score": 30, "passed": False, "reason": "菜系统计结果不精确，或与原始 CSV 数据不符。"})

    # Check 5: 使用大模型检查非结构化语义及正式基调 (10 pts)
    prompt_text = (
        "Does the following JSON report employ a formal, professional tone suitable for a federal officer's official record? "
        "The keys and any textual values should be professionally named (e.g., 'unauthorized_vehicles', 'cuisine_tally' rather than informal slang). "
        "Return YES if it reads like a formal digital report, NO if it contains overly casual/sloppy terms."
    )
    is_formal = llm_judge_content(prompt_text, json.dumps(json_data, indent=2))
    if is_formal:
        score_details.append({"item": "利用大模型检查报告基调", "score": 10, "max_score": 10, "passed": True, "reason": "大模型判定 JSON 结构具有官方报告的正式性"})
        total_score += 10
    else:
        score_details.append({"item": "利用大模型检查报告基调", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定报告基调不够正式或存在随意的键名命名"})

    # 汇总写入
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)

if __name__ == "__main__":
    main()
