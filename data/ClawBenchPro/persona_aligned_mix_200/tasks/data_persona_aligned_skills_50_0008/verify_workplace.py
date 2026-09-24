import os
import sys
import json
import httpx
from openai import OpenAI

# ---------------------------------------------------------
# 【强制 API 规范】初始化 LLM 客户端
# ---------------------------------------------------------
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
    """
    统一的非结构化文本大模型检测接口
    用于检测 Agent 是否违反了“别长篇大论给我分析”的指令，留下了多余的废话。
    """
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
# 核心验证逻辑
# ---------------------------------------------------------
def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "reports", "bottleneck.json")
    
    total_score = 0
    details = []

    # 1. 检查文件是否存在 (20分)
    if not os.path.exists(report_path):
        details.append({"item": "检查交付物文件是否存在", "score": 0, "max_score": 20, "passed": False, "reason": f"未找到文件: {report_path}"})
        write_score(0, details, workspace)
        return
    else:
        details.append({"item": "检查交付物文件是否存在", "score": 20, "max_score": 20, "passed": True, "reason": "文件存在"})
        total_score += 20

    # 读取文件内容
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    # 2. 检查 JSON 格式与 Schema 合法性 (30分)
    parsed_json = None
    try:
        parsed_json = json.loads(content)
        if not isinstance(parsed_json, dict):
            raise ValueError("Root element is not a dictionary.")
        
        if "bottleneck_entity" not in parsed_json:
            details.append({"item": "检查 JSON Schema", "score": 0, "max_score": 30, "passed": False, "reason": "JSON 中缺失核心键值 `bottleneck_entity`"})
        else:
            # 检查是否有捏造多余字段
            if len(parsed_json.keys()) > 1:
                details.append({"item": "检查 JSON Schema", "score": 10, "max_score": 30, "passed": False, "reason": "JSON 格式正确但包含多余捏造字段，严重扣分"})
                total_score += 10
            else:
                details.append({"item": "检查 JSON Schema", "score": 30, "max_score": 30, "passed": True, "reason": "JSON 格式完美，Schema 干净且合法"})
                total_score += 30
    except Exception as e:
        # 如果不是合法 JSON，使用 LLM 判断是否包含了大量的分析废话
        is_verbose = llm_judge_content("Does the following content contain conversational text, explanations, or long-winded analysis instead of just a pure data representation?", content)
        if is_verbose:
            details.append({"item": "检查 JSON Schema", "score": 0, "max_score": 30, "passed": False, "reason": f"解析失败 ({e})，且 LLM 判定包含长篇大论的废话，严重违反指令"})
        else:
            details.append({"item": "检查 JSON Schema", "score": 5, "max_score": 30, "passed": False, "reason": f"解析失败 ({e})，格式不合规，但未写废话"})
        total_score += 5

    # 3. 检查核心计算结果/数值精准度 (50分)
    # Target Entity ID should be "8847291" (extracted from Cloud Symbol Decoder)
    if parsed_json and "bottleneck_entity" in parsed_json:
        entity_val = str(parsed_json["bottleneck_entity"]).strip()
        if entity_val == "8847291":
            details.append({"item": "验证最终 Entity ID 结果", "score": 50, "max_score": 50, "passed": True, "reason": "成功提取出正确的实体 ID: 8847291"})
            total_score += 50
        else:
            details.append({"item": "验证最终 Entity ID 结果", "score": 0, "max_score": 50, "passed": False, "reason": f"实体 ID 错误，预期 '8847291'，实际为 '{entity_val}'。存在幻觉或使用了错误的数据源"})
    else:
        # 即使 JSON 解析失败，也严禁使用正则模糊提取结构化数据去给分，代码必须严格执行。未通过结构化提取，直接 0 分。
        details.append({"item": "验证最终 Entity ID 结果", "score": 0, "max_score": 50, "passed": False, "reason": "由于 JSON 解析失败或缺失键值，无法确定性地提取实体 ID，不予给分"})

    # 写入最终得分
    write_score(total_score, details, workspace)

def write_score(total_score, details, workspace):
    result = {
        "total_score": total_score,
        "details": details
    }
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Validation completed. Total Score: {total_score}")

if __name__ == "__main__":
    main()
