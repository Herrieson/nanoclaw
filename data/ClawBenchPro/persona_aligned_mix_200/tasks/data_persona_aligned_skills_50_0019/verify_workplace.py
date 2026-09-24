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
    """
    调用 LLM 判定结构化数据是否纯净，无多余的对话废话或幻觉字段
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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_file = os.path.join(workspace, "fix_list", "target.json")
    
    score = 0
    details = []
    
    # 1. 检查物理文件目录与文件是否存在 (15分)
    if os.path.isfile(target_file):
        score += 15
        details.append({"item": "检查目标文件是否存在", "score": 15, "max_score": 15, "passed": True, "reason": "文件 fix_list/target.json 存在且是普通文件"})
    else:
        reason = "文件 fix_list/target.json 不存在" if not os.path.exists(target_file) else "fix_list/target.json 是目录或非普通文件"
        details.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 15, "passed": False, "reason": reason})
        # 核心文件不存在，后续验证无意义
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": score, "details": details}, f, indent=2, ensure_ascii=False)
        return

    # 2. 检查 JSON Schema / 语法合法性 (20分)
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        score += 20
        details.append({"item": "检查 JSON 格式合法性", "score": 20, "max_score": 20, "passed": True, "reason": "target.json 是合法的 JSON 格式"})
    except json.JSONDecodeError:
        details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 20, "passed": False, "reason": "target.json 存在语法错误，无法解析为 JSON"})
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": score, "details": details}, f, indent=2, ensure_ascii=False)
        return

    # 3. 检查键值存在性 - 避免结构化数据幻觉 (15分)
    if "culprit_asset" in data:
        score += 15
        details.append({"item": "检查是否包含 culprit_asset 字段", "score": 15, "max_score": 15, "passed": True, "reason": "找到了指定的 culprit_asset 字段"})
    else:
        details.append({"item": "检查是否包含 culprit_asset 字段", "score": 0, "max_score": 15, "passed": False, "reason": "缺失题干要求的 culprit_asset 字段"})

    # 4. 核心计算结果 / 数据精准提取验证 (40分) - 必须依赖原生确定性代码
    asset_val = str(data.get("culprit_asset", ""))
    expected_path = "environments/ruins/statue_shattered_piece_04_cinematic.mesh"
    
    if asset_val == expected_path:
        score += 40
        details.append({"item": "检查提取的资产路径精确度", "score": 40, "max_score": 40, "passed": True, "reason": "资产路径严格、精确匹配"})
    elif "statue_shattered_piece_04_cinematic" in asset_val:
        # 部分匹配，如丢失了目录或包含了多余的标点
        score += 20
        details.append({"item": "检查提取的资产路径精确度", "score": 20, "max_score": 40, "passed": False, "reason": "资产路径部分匹配，但不够精确或附带了冗余字符"})
    else:
        details.append({"item": "检查提取的资产路径精确度", "score": 0, "max_score": 40, "passed": False, "reason": f"资产路径错误，未指向真正的导致崩溃的高顶点资产。当前值: {asset_val}"})

    # 5. LLM 判断附加字段与废话 (10分) - 严查 Agent 乱加戏
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            raw_content = f.read()
            
        prompt = (
            "Evaluate if the JSON content is strictly minimal and focused ONLY on outputting the requested key 'culprit_asset'. "
            "It should NOT contain hallucinated extra debugging fields (like vtx_count, entity_id, reasons, logs, or apologies). "
            "Does it look pure and free of unnecessary AI conversational bloat or extra keys? Answer YES or NO."
        )
        is_clean = llm_judge_content(prompt, raw_content)
        if is_clean:
            score += 10
            details.append({"item": "大模型检查冗余字段与幻觉", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 结构精简纯粹，无多余捏造字段"})
        else:
            details.append({"item": "大模型检查冗余字段与幻觉", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 包含多余的自我加戏字段或 AI 废话，不够严谨"})
    except Exception as e:
        details.append({"item": "大模型检查冗余字段与幻觉", "score": 0, "max_score": 10, "passed": False, "reason": f"LLM 调用失败: {e}"})

    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
