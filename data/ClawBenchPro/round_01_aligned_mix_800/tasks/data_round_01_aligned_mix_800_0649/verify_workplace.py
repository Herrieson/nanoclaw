import os
import sys
import json
import httpx
from openai import OpenAI

# 强制 API 规范
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
    report_path = os.path.join(workspace, "reports", "final_audit.json")
    
    score_details = []
    total_score = 0
    
    # 1. 结构与格式验证 (20分)
    file_exists = os.path.exists(report_path)
    if not file_exists:
        score_details.append({"item": "检查最终报告文件是否存在", "score": 0, "max_score": 20, "passed": False, "reason": f"未找到 {report_path}"})
        _write_score(0, score_details)
        return

    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            content_str = f.read()
            report_data = json.loads(content_str)
        score_details.append({"item": "检查文件是否为合法的JSON", "score": 20, "max_score": 20, "passed": True, "reason": "成功解析JSON"})
        total_score += 20
    except Exception as e:
        score_details.append({"item": "检查文件是否为合法的JSON", "score": 0, "max_score": 20, "passed": False, "reason": f"JSON解析失败: {e}"})
        _write_score(0, score_details)
        return

    # 2. 关键数值精确提取：流失的Bleach数量 (30分)
    # 正确逻辑: monday (1) + midweek (3) = 4
    content_dump = json.dumps(report_data, ensure_ascii=False)
    has_missing_room_data = False
    
    # 因为我们不确定Agent采用的结构，所以遍历所有的基础值检查关键数字，同时防止正则模糊匹配
    # 要求JSON的值中明确出现 4 (作为流失总量)，或者以某种形式记录了 1 和 3
    values = []
    def extract_values(obj):
        if isinstance(obj, dict):
            for v in obj.values():
                extract_values(v)
        elif isinstance(obj, list):
            for v in obj:
                extract_values(v)
        else:
            values.append(str(obj))
            
    extract_values(report_data)
    
    if "4" in values or ("1" in values and "3" in values):
        score_details.append({"item": "准确提取无房间Bleach消耗量", "score": 30, "max_score": 30, "passed": True, "reason": "在结构化数据中找到了正确的流失消耗数值(4或1和3明细)"})
        total_score += 30
        has_missing_room_data = True
    else:
        score_details.append({"item": "准确提取无房间Bleach消耗量", "score": 0, "max_score": 30, "passed": False, "reason": "未能在JSON独立值中找到准确的流失量数据(4)"})

    # 3. 关键数值精确提取：库存差异计算 (30分)
    # 正确逻辑: 总消耗 9, 库存减少 7, 差异为 2
    if "2" in values:
        score_details.append({"item": "准确计算并报告库存差异量", "score": 30, "max_score": 30, "passed": True, "reason": "在结构化数据中找到了正确的库存差异量(2)"})
        total_score += 30
    else:
        score_details.append({"item": "准确计算并报告库存差异量", "score": 0, "max_score": 30, "passed": False, "reason": "未能计算出正确的差异数字(2)"})

    # 4. LLM 验证语义：结构命名是否具有业务意义，且没有闲聊废话 (20分)
    prompt = """
    Check the JSON structure and keys. 
    1. Does it use professional and clear keys (e.g., 'missing_logs', 'inventory_discrepancy', 'lost_items') to describe the data?
    2. Does it STRICTLY EXCLUDE irrelevant chatters, such as mentioning birds, woodpeckers, or personal complaints?
    If both conditions are met, answer YES. Otherwise, answer NO.
    """
    if llm_judge_content(prompt, content_dump):
        score_details.append({"item": "大模型检查JSON业务语义", "score": 20, "max_score": 20, "passed": True, "reason": "JSON键名专业且未包含闲聊内容"})
        total_score += 20
    else:
        score_details.append({"item": "大模型检查JSON业务语义", "score": 0, "max_score": 20, "passed": False, "reason": "字段命名缺乏业务意义，或混入了与数据无关的闲聊"})

    _write_score(total_score, score_details)

def _write_score(total_score, details):
    out_data = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2, ensure_ascii=False)
    print(f"Evaluation finished. Total score: {total_score}")

if __name__ == "__main__":
    verify()
