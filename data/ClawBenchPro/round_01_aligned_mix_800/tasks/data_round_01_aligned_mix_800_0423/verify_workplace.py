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
    report_file = os.path.join(workspace, "store_report", "reconciliation_final.json")
    
    score_details = []
    total_score = 0

    # 1. Check directory and file existence (20 points)
    if os.path.exists(report_file):
        total_score += 20
        score_details.append({"item": "检查结果文件是否存在", "score": 20, "max_score": 20, "passed": True, "reason": "reconciliation_final.json 存在"})
    else:
        score_details.append({"item": "检查结果文件是否存在", "score": 0, "max_score": 20, "passed": False, "reason": "未找到 reconciliation_final.json"})
        # 无法继续
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 2. Check JSON validity (10 points)
    try:
        with open(report_file, "r") as f:
            data = json.load(f)
        total_score += 10
        score_details.append({"item": "检查结果是否为合法JSON", "score": 10, "max_score": 10, "passed": True, "reason": "JSON格式合法"})
    except Exception as e:
        score_details.append({"item": "检查结果是否为合法JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {e}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 将 JSON 扁平化成字符串用于粗略的内容分析（提取所有字符串内容）
    all_strings = " ".join([str(v) for k, v in data.items() if isinstance(v, str)])
    
    # 3. Check Total Missing Amount (40 points)
    # The expected total missing amount is exactly 460.0
    found_amount = False
    amount_score = 0
    # 尝试在顶层或任意一层寻找数值 460
    # 由于不确定 Agent 使用的精确键名，我们需要智能扫描 JSON 的数值
    def find_460(obj):
        if isinstance(obj, dict):
            for v in obj.values():
                if find_460(v): return True
        elif isinstance(obj, list):
            for v in obj:
                if find_460(v): return True
        elif isinstance(obj, (int, float)):
            if abs(obj - 460.0) < 0.01: return True
        return False

    if find_460(data):
        amount_score = 40
        total_score += 40
        score_details.append({"item": "核对被盗/缺失总金额", "score": 40, "max_score": 40, "passed": True, "reason": "成功计算出精确缺失金额 460.00 USD"})
    else:
        score_details.append({"item": "核对被盗/缺失总金额", "score": 0, "max_score": 40, "passed": False, "reason": "未能找到正确的金额 (460.00)"})

    # 4. Check Shorted Items List (30 points)
    # Expected shorted items: AVO-01, MAN-09, SAF-88
    # Should NOT contain: SOU-02, TRF-05, TOM-99
    json_str = json.dumps(data)
    expected_items = ["AVO-01", "MAN-09", "SAF-88"]
    unexpected_items = ["SOU-02", "TRF-05", "TOM-99"]
    
    has_all_expected = all(item in json_str for item in expected_items)
    has_any_unexpected = any(item in json_str for item in unexpected_items)
    
    if has_all_expected and not has_any_unexpected:
        total_score += 30
        score_details.append({"item": "核对缺失物品清单", "score": 30, "max_score": 30, "passed": True, "reason": "精准提取了所有缺失的SKU并排除了正常/多余的SKU"})
    elif has_all_expected and has_any_unexpected:
        total_score += 10
        score_details.append({"item": "核对缺失物品清单", "score": 10, "max_score": 30, "passed": False, "reason": "包含了缺失的SKU，但也包含了未缺失的干扰SKU，过滤逻辑错误"})
    else:
        score_details.append({"item": "核对缺失物品清单", "score": 0, "max_score": 30, "passed": False, "reason": "未能正确列出所有缺失的SKU"})

    # Write final score
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)

if __name__ == "__main__":
    verify()
