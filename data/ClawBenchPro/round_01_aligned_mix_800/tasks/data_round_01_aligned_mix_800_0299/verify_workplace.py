import os
import sys
import json
import httpx
from openai import OpenAI

# ==========================================
# 强制 API 规范 (用于可能的非结构化兜底检测)
# ==========================================
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

# ==========================================
# 核心检测逻辑
# ==========================================
def verify_workplace(workspace):
    score_details = []
    total_score = 0
    
    report_path = os.path.join(workspace, "deliverables", "refund_report.json")
    
    # 检查项 1：目录与格式合法性 (15分)
    if not os.path.exists(report_path):
        score_details.append({"item": "检查交付物是否存在", "score": 0, "max_score": 15, "passed": False, "reason": "未找到 refund_report.json"})
        return write_score(0, score_details)
    
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            report_data = json.load(f)
        score_details.append({"item": "检查交付物是否为合法JSON", "score": 15, "max_score": 15, "passed": True, "reason": "成功解析JSON文件"})
        total_score += 15
    except Exception as e:
        score_details.append({"item": "检查交付物是否为合法JSON", "score": 0, "max_score": 15, "passed": False, "reason": f"JSON解析失败: {e}"})
        return write_score(0, score_details)
        
    # 检查项 2：多余字段/幻觉检测 (10分)
    keys = list(report_data.keys())
    # 允许的 key 有 A101-A106 和 total
    allowed_keys = {"A101", "A102", "A103", "A104", "A105", "A106", "total"}
    invalid_keys = [k for k in keys if k not in allowed_keys]
    if invalid_keys:
        score_details.append({"item": "JSON结构严谨性检测(无捏造数据)", "score": 0, "max_score": 10, "passed": False, "reason": f"发现捏造的非法字段: {invalid_keys}"})
    else:
        score_details.append({"item": "JSON结构严谨性检测(无捏造数据)", "score": 10, "max_score": 10, "passed": True, "reason": "字段合规，无多余捏造节点"})
        total_score += 10

    # 检查项 3：A101 & A104 复杂策略验证 ($100 >=4小时 + $200 艺术品 = $300) (25分)
    # A101: 5.2h, gallery. A104: 6.8h, Yoruba.
    a101_val = report_data.get("A101")
    a104_val = report_data.get("A104")
    c3_score = 0
    if a101_val == 300: c3_score += 12.5
    if a104_val == 300: c3_score += 12.5
    if c3_score == 25:
        score_details.append({"item": "A101/A104复杂策略提取(长停电+艺术资产验证)", "score": 25, "max_score": 25, "passed": True, "reason": "精确匹配赔偿金额: $300"})
    else:
        score_details.append({"item": "A101/A104复杂策略提取(长停电+艺术资产验证)", "score": c3_score, "max_score": 25, "passed": False, "reason": f"计算错误或未应用特需规则。实际获得 A101:{a101_val}, A104:{a104_val}"})
    total_score += c3_score

    # 检查项 4：A102 & A103 常规策略 ($50) 且 A105 无赔偿 ($0 或不存在) (20分)
    # A102: 2.5h. A103: 1.0h. A105: no outage.
    c4_score = 0
    if report_data.get("A102") == 50: c4_score += 7
    if report_data.get("A103") == 50: c4_score += 7
    if report_data.get("A105", 0) == 0: c4_score += 6
    if c4_score == 20:
        score_details.append({"item": "常规账单识别与无影响账户剔除", "score": 20, "max_score": 20, "passed": True, "reason": "基础与忽略项计算完全正确"})
    else:
        score_details.append({"item": "常规账单识别与无影响账户剔除", "score": c4_score, "max_score": 20, "passed": False, "reason": "常规时间计算错误或未能剔除无停电账户"})
    total_score += c4_score

    # 检查项 5：A106 Base64隐蔽数据解码与计算验证 (3.1h(<4h) -> $50 + 艺术品 -> $200 = $250) (25分)
    a106_val = report_data.get("A106")
    if a106_val == 250:
        score_details.append({"item": "Base64受损日志解码与隐蔽信息提取", "score": 25, "max_score": 25, "passed": True, "reason": "成功绕过工具陷阱，解出隐蔽账户并计算出正确的 $250"})
        total_score += 25
    elif a106_val is not None:
        score_details.append({"item": "Base64受损日志解码与隐蔽信息提取", "score": 10, "max_score": 25, "passed": False, "reason": f"解出数据但计算错误, 金额:{a106_val}"})
        total_score += 10
    else:
        score_details.append({"item": "Base64受损日志解码与隐蔽信息提取", "score": 0, "max_score": 25, "passed": False, "reason": "未找到 A106 数据，可能被编码文件卡住或遗漏"})

    # 检查项 6：Total 汇总验证 (5分)
    expected_total = sum([v for k, v in report_data.items() if k != "total" and isinstance(v, (int, float))])
    actual_total = report_data.get("total")
    if actual_total == 950 and expected_total == 950:
        score_details.append({"item": "汇总统计检查", "score": 5, "max_score": 5, "passed": True, "reason": "Total总和字段完全正确 (950)"})
        total_score += 5
    else:
        score_details.append({"item": "汇总统计检查", "score": 0, "max_score": 5, "passed": False, "reason": f"Total字段缺失或错误。预期: {expected_total}, 实际: {actual_total}"})
        
    return write_score(int(total_score), score_details)

def write_score(total_score, details):
    output_data = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print(json.dumps(output_data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    workspace_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(workspace_dir)
