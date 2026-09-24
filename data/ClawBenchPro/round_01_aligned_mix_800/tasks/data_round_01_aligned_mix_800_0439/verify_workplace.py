import os
import sys
import json
import httpx
import math
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
    
    score_details = []
    total_score = 0
    
    target_file = os.path.join(workspace, "deliverables", "summary.json")
    expected_file = os.path.join(workspace, ".expected_solution.json")
    
    # 1. 检查目标文件是否存在 (10 分)
    if os.path.exists(target_file):
        total_score += 10
        score_details.append({"item": "检查目标文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 deliverables/summary.json 存在"})
    else:
        score_details.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 deliverables/summary.json"})
        return dump_score(0, score_details)
        
    # 读取预期答案
    if not os.path.exists(expected_file):
        score_details.append({"item": "加载预期答案", "score": 0, "max_score": 0, "passed": False, "reason": "无法找到 .expected_solution.json，测试环境异常"})
        return dump_score(total_score, score_details)
        
    with open(expected_file, "r", encoding="utf-8") as f:
        expected_data = json.load(f)
        
    # 2. 检查 JSON 格式与 Schema合法性 (20 分)
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            agent_data = json.load(f)
            
        # 结构合法性校验 (10 分)
        if isinstance(agent_data, dict):
            total_score += 10
            score_details.append({"item": "检查 JSON 基本结构", "score": 10, "max_score": 10, "passed": True, "reason": "成功解析 JSON 对象"})
        else:
            score_details.append({"item": "检查 JSON 基本结构", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 根节点不是字典"})
            return dump_score(total_score, score_details)
            
        # 键值严格匹配校验 (10 分)
        expected_keys = {"total_approved_amount", "bird_watcher_names"}
        agent_keys = set(agent_data.keys())
        if agent_keys == expected_keys:
            total_score += 10
            score_details.append({"item": "检查键名是否严格合法", "score": 10, "max_score": 10, "passed": True, "reason": "只包含要求的两个键，无捏造或遗漏"})
        else:
            score_details.append({"item": "检查键名是否严格合法", "score": 0, "max_score": 10, "passed": False, "reason": f"键名不合规。预期: {expected_keys}, 实际: {agent_keys}"})
            
    except json.JSONDecodeError:
        score_details.append({"item": "检查 JSON 基本结构", "score": 0, "max_score": 20, "passed": False, "reason": "JSON 文件损坏或格式错误，无法解析"})
        return dump_score(total_score, score_details)
        
    # 3. 核心计算结果验证：总批准金额 (40 分)
    agent_amount = agent_data.get("total_approved_amount")
    expected_amount = expected_data.get("total_approved_amount")
    
    if isinstance(agent_amount, (int, float)):
        if math.isclose(agent_amount, expected_amount, abs_tol=0.01):
            total_score += 40
            score_details.append({"item": "验证总金额精确计算", "score": 40, "max_score": 40, "passed": True, "reason": f"总金额精确匹配预期值 {expected_amount}"})
        else:
            # 可能是没去重或包含了诱饵数据
            score_details.append({"item": "验证总金额精确计算", "score": 0, "max_score": 40, "passed": False, "reason": f"金额计算错误。可能是未去重或未正确过滤诱饵数据。预期: {expected_amount}, 实际: {agent_amount}"})
    else:
         score_details.append({"item": "验证总金额精确计算", "score": 0, "max_score": 40, "passed": False, "reason": "总金额类型错误，非数字"})

    # 4. 核心计算结果验证：违禁人员名单 (30 分)
    agent_names = agent_data.get("bird_watcher_names", [])
    expected_names = expected_data.get("bird_watcher_names", [])
    
    if isinstance(agent_names, list):
        if agent_names == expected_names:
            total_score += 30
            score_details.append({"item": "验证违禁人员名单及排序", "score": 30, "max_score": 30, "passed": True, "reason": "名单内容完全准确且按照字母序排序"})
        elif set(agent_names) == set(expected_names):
            total_score += 15
            score_details.append({"item": "验证违禁人员名单及排序", "score": 15, "max_score": 30, "passed": False, "reason": "名单集合一致，但未严格进行字母排序"})
        else:
            missing = set(expected_names) - set(agent_names)
            extra = set(agent_names) - set(expected_names)
            score_details.append({"item": "验证违禁人员名单及排序", "score": 0, "max_score": 30, "passed": False, "reason": f"名单错误。漏抓: {len(missing)}人，错抓: {len(extra)}人"})
    else:
        score_details.append({"item": "验证违禁人员名单及排序", "score": 0, "max_score": 30, "passed": False, "reason": "名单字段类型错误，非列表格式"})

    dump_score(total_score, score_details)

def dump_score(total, details):
    res = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
    return res

if __name__ == "__main__":
    verify()
