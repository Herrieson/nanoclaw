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
    语义内容检测接口（本任务核心目标为纯结构化数据，预留备用）
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

def verify(workspace):
    score = 0
    details = []

    target_dir = os.path.join(workspace, "triage")
    target_file = os.path.join(target_dir, "conflict_target.json")
    
    # 验证项 1: 结果文件存在性 (10分)
    if os.path.isfile(target_file):
        details.append({
            "item": "检查目标文件是否生成",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件 triage/conflict_target.json 已成功创建"
        })
        score += 10
    else:
        details.append({
            "item": "检查目标文件是否生成",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "未找到 triage/conflict_target.json 文件"
        })
        # 文件不存在，后续直接短路
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": score, "details": details}, f, indent=2, ensure_ascii=False)
        return

    # 验证项 2-5: 读取并解析结构化数据
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        
        # 验证项 2: JSON 字段合法性与幻觉剔除 (20分)
        required_keys = {"node_id", "conflict_term", "conflict_index"}
        actual_keys = set(data.keys())
        
        if not required_keys.issubset(actual_keys):
            details.append({
                "item": "检查 JSON Schema 完整性",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": f"结构不合法，缺少必需的字段: {required_keys - actual_keys}"
            })
        elif actual_keys != required_keys:
            details.append({
                "item": "检查 JSON Schema 完整性",
                "score": 10,
                "max_score": 20,
                "passed": False,
                "reason": f"包含冗余的幻觉字段: {actual_keys - required_keys}，扣除10分"
            })
            score += 10
        else:
            details.append({
                "item": "检查 JSON Schema 完整性",
                "score": 20,
                "max_score": 20,
                "passed": True,
                "reason": "严格包含了必需的三个字段，且无任何捏造冗余，格式完美"
            })
            score += 20
        
        # 验证项 3: node_id 多跳映射正确性 (25分)
        node_id = data.get("node_id")
        if node_id == "node-payment-beta":
            details.append({
                "item": "验证 node_id 溯源正确性",
                "score": 25,
                "max_score": 25,
                "passed": True,
                "reason": "成功避开 deprecated 路由表干扰，从正确的活跃网格映射出了正确的节点 ID"
            })
            score += 25
        else:
            details.append({
                "item": "验证 node_id 溯源正确性",
                "score": 0,
                "max_score": 25,
                "passed": False,
                "reason": f"node_id 错误（得到 '{node_id}'），说明 Agent 未匹配正确的活跃路由表或解析失败"
            })

        # 验证项 4: conflict_term 解码准确性 (20分)
        conflict_term = data.get("conflict_term")
        if isinstance(conflict_term, int) and conflict_term == 4:
            details.append({
                "item": "验证 RPC 载荷解码 - conflict_term",
                "score": 20,
                "max_score": 20,
                "passed": True,
                "reason": "Base64 payload 解码与 JSON 解析成功，conflict_term 提取正确"
            })
            score += 20
        else:
            details.append({
                "item": "验证 RPC 载荷解码 - conflict_term",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": f"conflict_term 数据错误 (期望值为 4，实际为 {conflict_term})"
            })

        # 验证项 5: conflict_index 解码准确性 (25分)
        conflict_index = data.get("conflict_index")
        if isinstance(conflict_index, int) and conflict_index == 100:
            details.append({
                "item": "验证 RPC 载荷解码 - conflict_index",
                "score": 25,
                "max_score": 25,
                "passed": True,
                "reason": "Base64 payload 解码与 JSON 解析成功，conflict_index 提取正确"
            })
            score += 25
        else:
            details.append({
                "item": "验证 RPC 载荷解码 - conflict_index",
                "score": 0,
                "max_score": 25,
                "passed": False,
                "reason": f"conflict_index 数据错误 (期望值为 100，实际为 {conflict_index})"
            })

    except json.JSONDecodeError:
        details.append({
            "item": "检查 JSON Schema 完整性",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "文件内容并非合法的 JSON 格式"
        })
        details.append({"item": "验证 node_id 溯源正确性", "score": 0, "max_score": 25, "passed": False, "reason": "文件解析失败，无法验证"})
        details.append({"item": "验证 RPC 载荷解码 - conflict_term", "score": 0, "max_score": 20, "passed": False, "reason": "文件解析失败，无法验证"})
        details.append({"item": "验证 RPC 载荷解码 - conflict_index", "score": 0, "max_score": 25, "passed": False, "reason": "文件解析失败，无法验证"})

    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
