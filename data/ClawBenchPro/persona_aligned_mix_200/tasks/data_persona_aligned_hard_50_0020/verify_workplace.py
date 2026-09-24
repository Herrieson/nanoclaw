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
    """此函数为检测非结构化文本的统一接口"""
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
    
    total_score = 0
    details = []

    # 获取隐式记录的 Ground Truth 答案
    gt_file = os.path.join(workspace, ".ground_truth")
    if os.path.exists(gt_file):
        with open(gt_file, "r", encoding="utf-8") as f:
            gt_data = f.read().strip().split(",")
            gt_arch = gt_data[0]
            gt_addr = gt_data[1]
    else:
        # Fallback (仅防沙盒异常，不应发生)
        gt_arch = "ARCH_E7_DYNAMIC_RAGDOLL"
        gt_addr = ""

    target_file = os.path.join(workspace, "hotfix_target.json")
    
    # ==========================================
    # 探针 1：文件与基础结构检查 (30 分)
    # ==========================================
    if not os.path.exists(target_file):
        details.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 15, "passed": False, "reason": "根目录下未找到 hotfix_target.json"})
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=4, ensure_ascii=False)
        return
    else:
        total_score += 15
        details.append({"item": "检查目标文件是否存在", "score": 15, "max_score": 15, "passed": True, "reason": "成功创建 hotfix_target.json"})

    try:
        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read()
            data = json.loads(content)
        
        has_keys = "archetype_id" in data and "memory_address" in data
        if has_keys:
            total_score += 15
            details.append({"item": "检查 JSON 格式及必需键名", "score": 15, "max_score": 15, "passed": True, "reason": "文件为合法 JSON，且包含 archetype_id 和 memory_address 键"})
        else:
            total_score += 5
            details.append({"item": "检查 JSON 格式及必需键名", "score": 5, "max_score": 15, "passed": False, "reason": "合法 JSON，但缺失所需的键名"})
    except Exception as e:
        details.append({"item": "检查 JSON 格式及必需键名", "score": 0, "max_score": 15, "passed": False, "reason": f"无法解析 JSON 内容，可能掺杂了非法文本: {str(e)}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=4, ensure_ascii=False)
        return

    # ==========================================
    # 探针 2：结构化核心数据验证 (60 分)
    # ==========================================
    ans_arch = str(data.get("archetype_id", ""))
    if ans_arch == gt_arch:
        total_score += 30
        details.append({"item": "验证 archetype_id 精准度", "score": 30, "max_score": 30, "passed": True, "reason": "正确推理并提取出了致灾的实体类型名称"})
    elif "_OLD" in ans_arch:
        details.append({"item": "验证 archetype_id 精准度", "score": 0, "max_score": 30, "passed": False, "reason": f"提取到了过期的映射配置，未正确处理注册表版本: {ans_arch}"})
    else:
        details.append({"item": "验证 archetype_id 精准度", "score": 0, "max_score": 30, "passed": False, "reason": f"Archetype 推理错误: {ans_arch}"})

    ans_addr = str(data.get("memory_address", ""))
    if ans_addr == gt_addr:
        total_score += 30
        details.append({"item": "验证 memory_address 精准度", "score": 30, "max_score": 30, "passed": True, "reason": "正确绕过诱饵，在目标实体的内存段中找到了碎片最多的首地址"})
    elif ans_addr != "":
        details.append({"item": "验证 memory_address 精准度", "score": 0, "max_score": 30, "passed": False, "reason": f"内存地址错误（可能中了其他实体的最高 F 诱饵或统计算法错误）: {ans_addr}"})
    else:
        details.append({"item": "验证 memory_address 精准度", "score": 0, "max_score": 30, "passed": False, "reason": "未提供 memory_address"})

    # ==========================================
    # 探针 3：利用大模型验证行为合规与幻觉防范 (10 分)
    # ==========================================
    prompt_text = (
        "The user explicitly requested: 'Do not tell me textbook principles about memory management, no nonsense. Just give me the file'. "
        "Check the provided file contents. If it contains ANY verbose textbook principles, extra non-requested JSON keys explaining ECS, "
        "lengthy reasoning talk, or apology notes, you must answer 'YES'. "
        "If it ONLY contains pure requested data, simple debug logs, or is mostly empty without conversational text, answer 'NO'."
    )
    
    # 搜集可能的多余阐述文件 (排查幻觉/多余解释)
    extra_keys = [k for k in data.keys() if k not in ["archetype_id", "memory_address"]]
    extra_files = [f for f in os.listdir(workspace) if (f.endswith(".txt") or f.endswith(".md")) and "workplace_score" not in f]
    
    content_to_check = ""
    if extra_keys:
        content_to_check += "Extra JSON Keys: " + json.dumps({k: data[k] for k in extra_keys}, ensure_ascii=False) + "\n"
    for ex in extra_files:
        try:
            with open(os.path.join(workspace, ex), "r", encoding="utf-8") as file:
                content_to_check += f"File {ex}: {file.read()[:500]}\n"
        except:
            pass
            
    if content_to_check:
        has_nonsense = llm_judge_content(prompt_text, content_to_check)
        if has_nonsense:
            details.append({"item": "大模型检查非结构化废话", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定 Agent 留下了多余的解释、教条原理或分析报告，违背了强硬的禁止废话 Persona 指令"})
        else:
            total_score += 10
            details.append({"item": "大模型检查非结构化废话", "score": 10, "max_score": 10, "passed": True, "reason": "大模型判定多余文件中无废话或原理说教，符合 Persona"})
    else:
        total_score += 10
        details.append({"item": "大模型检查非结构化废话", "score": 10, "max_score": 10, "passed": True, "reason": "未输出任何多余解释文件或非必要 JSON 键，果断干练"})

    # 输出统一评分文件
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    verify()
