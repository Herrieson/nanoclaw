import os
import sys
import json
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

def extract_worker_info(data, worker_name):
    """
    深度优先搜索，寻找包含特定工人名称的字典或节点
    以应对不同 Agent 生成的不同结构的 JSON
    """
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(k, str) and worker_name.lower() in k.lower():
                return v
        for k, v in data.items():
            if isinstance(v, str) and worker_name.lower() in v.lower():
                return data
            res = extract_worker_info(v, worker_name)
            if res is not None:
                return res
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, str) and worker_name.lower() in item.lower():
                return item
            res = extract_worker_info(item, worker_name)
            if res is not None:
                return res
    return None

def find_numeric_value(data, keywords):
    """
    在节点中寻找特定关键字对应的数值
    """
    if isinstance(data, dict):
        for k, v in data.items():
            if any(kw in k.lower() for kw in keywords):
                if isinstance(v, (int, float)):
                    return v
                if isinstance(v, str) and v.isdigit():
                    return int(v)
        # 如果第一层没找到，尝试在所有值中寻找字典
        for v in data.values():
            val = find_numeric_value(v, keywords)
            if val is not None:
                return val
    return None

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "reports", "final_summary.json")
    
    details = []
    total_score = 0
    
    # 1. 检查文件是否存在且格式合法 (15 分)
    score_exist = 0
    passed_exist = False
    reason_exist = "未找到 reports/final_summary.json 或格式不是有效 JSON"
    report_data = None
    
    if os.path.exists(report_path):
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                report_data = json.load(f)
            score_exist = 15
            passed_exist = True
            reason_exist = "JSON 文件存在且解析成功"
        except json.JSONDecodeError:
            reason_exist = "文件存在但非合法 JSON"
    
    details.append({"item": "检查结果文件是否存在且为合法 JSON", "score": score_exist, "max_score": 15, "passed": passed_exist, "reason": reason_exist})
    total_score += score_exist
    
    if report_data:
        # 2. 检查违规工人的识别 (25 分)
        score_unauthorized = 0
        passed_unauth = False
        unauth_target = ["jose ghost", "unknown_guy"]
        
        # 将 JSON 序列化为文本，使用 LLM 判别违规名单（涉及语义理解：因为 unauthorized 对应的 key 不定）
        report_text = json.dumps(report_data)
        prompt_unauth = (
            "Check if the JSON clearly categorizes both 'Jose Ghost' and 'Unknown_Guy' "
            "as unauthorized, invalid, or non-compliant workers. AND ensures NO other valid workers "
            "(Mateo Hernandez, Santiago Garcia, Luis Rodriguez, Carlos Martinez, Juan Lopez) are listed as unauthorized."
        )
        if llm_judge_content(prompt_unauth, report_text):
            score_unauthorized = 25
            passed_unauth = True
            reason_unauth = "成功识别出全部且仅限两位违规工人"
        else:
            reason_unauth = "未能正确分类违规工人（可能漏掉，或将合规工人误判）"
            
        details.append({"item": "利用大模型语义判断违规工人的识别准确性", "score": score_unauthorized, "max_score": 25, "passed": passed_unauth, "reason": reason_unauth})
        total_score += score_unauthorized
        
        # 3. 检查合规工人的数据准确性 (总共 60 分, 每人 12 分)
        target_stats = {
            "Mateo Hernandez": {"hours": 12, "pillars": 3},
            "Santiago Garcia": {"hours": 12, "pillars": 1},
            "Luis Rodriguez": {"hours": 10, "pillars": 0},
            "Carlos Martinez": {"hours": 8, "pillars": 3},
            "Juan Lopez": {"hours": 6, "pillars": 0}
        }
        
        for worker, stats in target_stats.items():
            worker_info = extract_worker_info(report_data, worker)
            if not worker_info:
                details.append({"item": f"提取 {worker} 的数据", "score": 0, "max_score": 12, "passed": False, "reason": "在 JSON 中未能找到该工人的信息节点"})
                continue
            
            hours = find_numeric_value(worker_info, ["hour", "hora", "time", "hr"])
            pillars = find_numeric_value(worker_info, ["pillar", "pilar", "roto", "material", "loss", "broken", "damage"])
            
            w_score = 0
            w_reason = []
            if hours == stats["hours"]:
                w_score += 6
                w_reason.append("工时计算正确")
            else:
                w_reason.append(f"工时错误 (应为 {stats['hours']}, 实际找到 {hours})")
                
            if pillars == stats["pillars"]:
                w_score += 6
                w_reason.append("损耗计算正确")
            else:
                w_reason.append(f"损耗错误 (应为 {stats['pillars']}, 实际找到 {pillars})")
                
            details.append({"item": f"提取并校验 {worker} 的准确数据", "score": w_score, "max_score": 12, "passed": (w_score == 12), "reason": ", ".join(w_reason)})
            total_score += w_score

    else:
        # 如果无法解析 JSON，后续直接 0 分
        details.append({"item": "违规工人识别", "score": 0, "max_score": 25, "passed": False, "reason": "文件无效"})
        details.append({"item": "合规工人数据准确性", "score": 0, "max_score": 60, "passed": False, "reason": "文件无效"})

    # 输出最终评分 JSON
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
