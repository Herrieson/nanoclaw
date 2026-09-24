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
    """大模型语义辅助检查接口"""
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
    target_file = os.path.join(workspace, "hotfix_target.json")
    
    total_score = 0
    details = []

    # ----------------------------------------------------
    # Item 1: 检查结果文件是否存在 (10分)
    # ----------------------------------------------------
    item1 = {"item": "检查 hotfix_target.json 文件是否存在", "max_score": 10, "score": 0, "passed": False, "reason": ""}
    if os.path.exists(target_file):
        item1["score"] = 10
        item1["passed"] = True
        item1["reason"] = "目标文件存在。"
        total_score += 10
    else:
        item1["reason"] = "未找到 hotfix_target.json 文件。"
        details.append(item1)
        details.append({"item": "检查 JSON 格式合法性", "max_score": 10, "score": 0, "passed": False, "reason": "文件不存在，跳过。"})
        details.append({"item": "校验核心字段 archetype_id", "max_score": 30, "score": 0, "passed": False, "reason": "文件不存在，跳过。"})
        details.append({"item": "校验核心字段 memory_address", "max_score": 30, "score": 0, "passed": False, "reason": "文件不存在，跳过。"})
        details.append({"item": "大模型校验内容是否废话", "max_score": 20, "score": 0, "passed": False, "reason": "文件不存在，跳过。"})
        output_result(total_score, details, workspace)
        return

    details.append(item1)

    # ----------------------------------------------------
    # Item 2: 检查是否为合法 JSON 对象 (10分)
    # ----------------------------------------------------
    item2 = {"item": "检查 JSON 格式合法性", "max_score": 10, "score": 0, "passed": False, "reason": ""}
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            file_content = f.read()
            data = json.loads(file_content)
        item2["score"] = 10
        item2["passed"] = True
        item2["reason"] = "成功解析并加载为有效 JSON 结构。"
        total_score += 10
    except json.JSONDecodeError:
        item2["reason"] = "文件内容并不是一个有效的 JSON，无法反序列化。"
        details.append(item2)
        details.append({"item": "校验核心字段 archetype_id", "max_score": 30, "score": 0, "passed": False, "reason": "格式错误，跳过提取。"})
        details.append({"item": "校验核心字段 memory_address", "max_score": 30, "score": 0, "passed": False, "reason": "格式错误，跳过提取。"})
        details.append({"item": "大模型校验内容是否废话", "max_score": 20, "score": 0, "passed": False, "reason": "格式错误，跳过提取。"})
        output_result(total_score, details, workspace)
        return
        
    details.append(item2)

    if not isinstance(data, dict):
        data = {} # 如果是数组或其它结构，作空字典处理，交由下方结构校验扣分

    # ----------------------------------------------------
    # Item 3: 精准提取 archetype_id (30分)
    # ----------------------------------------------------
    item3 = {"item": "校验核心字段 archetype_id", "max_score": 30, "score": 0, "passed": False, "reason": ""}
    arch_val = data.get("archetype_id", "")
    target_arch = "ARCH_E7_DYNAMIC_MESH"
    
    if str(arch_val).strip() == target_arch:
        item3["score"] = 30
        item3["passed"] = True
        item3["reason"] = "准确无误地提炼并命中了正确的 archetype_id。"
        total_score += 30
    elif target_arch in str(data):
        # 模糊保护分，说明查到了但没有按规范填 key
        item3["score"] = 10
        item3["passed"] = False
        item3["reason"] = "提取了正确的归因 ID，但未严格通过 'archetype_id' 为 key 写入 JSON 对象。"
        total_score += 10
    else:
        item3["reason"] = f"未找到导致卡顿的正确 Archetype，期望是 {target_arch}。"
    details.append(item3)

    # ----------------------------------------------------
    # Item 4: 精准提取 memory_address (30分)
    # ----------------------------------------------------
    item4 = {"item": "校验核心字段 memory_address", "max_score": 30, "score": 0, "passed": False, "reason": ""}
    mem_val = data.get("memory_address", "")
    target_mem = "0x000002B47C90F000"
    
    if str(mem_val).strip().lower() == target_mem.lower():
        item4["score"] = 30
        item4["passed"] = True
        item4["reason"] = "准确获取并记录了该对象最高碎片的内存段首地址。"
        total_score += 30
    elif target_mem.lower() in str(data).lower():
        item4["score"] = 10
        item4["passed"] = False
        item4["reason"] = "提取了正确的内存地址，但未严格通过 'memory_address' 为 key 写入 JSON 对象。"
        total_score += 10
    else:
        item4["reason"] = f"内存地址查找错误，或者云端分析获取失败。"
    details.append(item4)

    # ----------------------------------------------------
    # Item 5: LLM 检查是否遵循业务要求“不带废话原理” (20分)
    # ----------------------------------------------------
    item5 = {"item": "大模型校验内容是否废话", "max_score": 20, "score": 0, "passed": False, "reason": ""}
    prompt_desc = (
        "The user explicitly commanded: '别跟我废话那些内存管理的教科书原理，我只要那个 ID 和地址'."
        "Does the provided JSON output strictly contain ONLY the required variables without any lengthy conversational explanations, reasoning, or textbook principles?"
    )
    is_concise = llm_judge_content(prompt_desc, file_content)
    if is_concise:
        item5["score"] = 20
        item5["passed"] = True
        item5["reason"] = "大模型判定 JSON 输出精简，严格遵循了不废话的要求。"
        total_score += 20
    else:
        item5["reason"] = "大模型判定内容中包含了被明令禁止的多余解释性废话或原理描述。"
    details.append(item5)

    # 输出结果
    output_result(total_score, details, workspace)

def output_result(total_score, details, workspace):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
