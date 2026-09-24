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
    """大模型统一检测接口，仅返回 YES/NO"""
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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "office_reports", "transmission_summary.json")
    
    total_score = 0
    details = []
    
    # 1. 检查目标目录与文件是否存在 (20分)
    file_exists = os.path.isfile(report_path)
    if file_exists:
        score = 20
        total_score += score
        details.append({"item": "检查目标文件是否存在", "score": score, "max_score": 20, "passed": True, "reason": "transmission_summary.json 文件存在"})
    else:
        details.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 20, "passed": False, "reason": "未找到 office_reports/transmission_summary.json 文件"})
        
    # 如果文件不存在，后续验证无法进行
    if not file_exists:
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 2. 检查 JSON 格式的合法性 (20分)
    json_data = None
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            raw_content = f.read()
            json_data = json.loads(raw_content)
            
        score = 20
        total_score += score
        details.append({"item": "检查 JSON 格式合法性", "score": score, "max_score": 20, "passed": True, "reason": "文件是合法的 JSON 格式"})
    except Exception as e:
        details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 20, "passed": False, "reason": f"JSON 解析失败: {e}"})

    if json_data is not None:
        # 3. 使用大模型检查 JSON 的 Key 语义和是否包含无用废话 (20分)
        # Agent 不应包含如 "message", "explanation" 等多余字段
        keys_str = ", ".join(json_data.keys()) if isinstance(json_data, dict) else ""
        prompt = (
            "Evaluate the JSON keys provided. The keys must strictly represent 'transmission labor hours' "
            "and 'transmission fluid quarts'. There should be NO extra explanatory keys (like 'message', 'note', 'status'). "
            "Are the keys clean, compliant, and strictly representing only the requested variables?"
        )
        if isinstance(json_data, dict) and llm_judge_content(prompt, keys_str):
            score = 20
            total_score += score
            details.append({"item": "检查 JSON 字段语义合法性", "score": score, "max_score": 20, "passed": True, "reason": "大模型判定 JSON 的键只包含核心所需指标且无冗余说明"})
        else:
            details.append({"item": "检查 JSON 字段语义合法性", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定字段包含冗余/无关信息，或者格式不是对象"})

        # 4. 严密代码解析数值：劳动时间 = 18小时，变速箱油 = 25夸脱 (40分, 各20分)
        # 为了防范键名不一致的问题，提取所有数值并判断
        numeric_values = []
        if isinstance(json_data, dict):
            for v in json_data.values():
                if isinstance(v, (int, float)):
                    numeric_values.append(v)
                elif isinstance(v, str) and v.replace('.', '', 1).isdigit():
                    numeric_values.append(float(v))

        # Check for hours = 18
        if 18 in numeric_values or 18.0 in numeric_values:
            score = 20
            total_score += score
            details.append({"item": "精准验证工时数据", "score": score, "max_score": 20, "passed": True, "reason": "正确提取到总计 18 小时的变速箱维修工时 (12+2+4)"})
        else:
            details.append({"item": "精准验证工时数据", "score": 0, "max_score": 20, "passed": False, "reason": "未能计算出正确的 18 小时工时 (可能误入了引擎/火花塞时间)"})

        # Check for fluid = 25
        if 25 in numeric_values or 25.0 in numeric_values:
            score = 20
            total_score += score
            details.append({"item": "精准验证变速箱油数据", "score": score, "max_score": 20, "passed": True, "reason": "正确提取到总计 25 夸脱的变速箱油用量 (8+14+3)"})
        else:
            details.append({"item": "精准验证变速箱油数据", "score": 0, "max_score": 20, "passed": False, "reason": "未能计算出正确的 25 夸脱变速箱油 (可能误入了机油数据)"})

    # 输出最终成绩
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
