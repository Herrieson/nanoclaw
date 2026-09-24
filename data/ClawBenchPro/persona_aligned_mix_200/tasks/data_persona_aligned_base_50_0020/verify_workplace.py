import os
import sys
import json
import httpx
from openai import OpenAI

# ----------------- 强制 API 规范 -----------------
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
    """大模型语义检测接口，只用于检测自然语言语义/格式外废话"""
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
# -------------------------------------------------

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_file = os.path.join(workspace, "hotfix_target.json")
    
    score_details = []
    total_score = 0
    
    # Check 1: 检查物理文件是否存在 (15分)
    if os.path.exists(target_file):
        total_score += 15
        score_details.append({
            "item": "检查 hotfix_target.json 文件是否存在",
            "score": 15, "max_score": 15, "passed": True,
            "reason": "目标文件 hotfix_target.json 存在"
        })
    else:
        score_details.append({
            "item": "检查 hotfix_target.json 文件是否存在",
            "score": 0, "max_score": 15, "passed": False,
            "reason": "未找到 hotfix_target.json 文件"
        })
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)
        return

    # Check 2: 检查文件格式及其内容结构 (15分)
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        total_score += 15
        score_details.append({
            "item": "检查文件是否为合法 JSON",
            "score": 15, "max_score": 15, "passed": True,
            "reason": "成功以 JSON 格式解析文件"
        })
    except json.JSONDecodeError:
        score_details.append({
            "item": "检查文件是否为合法 JSON",
            "score": 0, "max_score": 15, "passed": False,
            "reason": "JSON 格式非法或存在语法错误"
        })
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)
        return

    # 附加语义检测：检查是否违背“不要废话内存管理原理”的指令
    # 提取多余的文本字段或过长的注释值交由 LLM 判别
    has_waste_talk = False
    for key, value in data.items():
        if isinstance(value, str) and len(value) > 30 and key not in ["archetype_id", "memory_address"]:
            prompt = "Does the following text contain unsolicited textbook-style explanations or tutorials about computer memory management or ECS principles? If yes, answer 'YES', else 'NO'."
            if llm_judge_content(prompt, value):
                has_waste_talk = True
                break
                
    if has_waste_talk:
        # 一票否决性质的倒扣分
        total_score = max(0, total_score - 10)
        score_details.append({
            "item": "严格遵守禁止说教的要求",
            "score": -10, "max_score": 0, "passed": False,
            "reason": "检测到多余的内存管理教科书原理解释（幻觉或违背 Persona），倒扣 10 分"
        })
    else:
        score_details.append({
            "item": "严格遵守禁止说教的要求",
            "score": 0, "max_score": 0, "passed": True,
            "reason": "输出干净简洁，未包含啰嗦的原理解释"
        })

    # Check 3: 精准检查 archetype_id 提取结果 (30分)
    arch_id = str(data.get("archetype_id", "")).strip()
    if arch_id == "ARCH_E7_DYNAMIC_MESH":
        total_score += 30
        score_details.append({
            "item": "检查 archetype_id 定位是否精准",
            "score": 30, "max_score": 30, "passed": True,
            "reason": "成功分析日志并提取出发生高延迟的 ARCH_E7_DYNAMIC_MESH"
        })
    else:
        score_details.append({
            "item": "检查 archetype_id 定位是否精准",
            "score": 0, "max_score": 30, "passed": False,
            "reason": f"提取错误。期望为 ARCH_E7_DYNAMIC_MESH，实际为: '{arch_id}'"
        })

    # Check 4: 精准检查 memory_address 提取结果并排查诱饵陷阱 (40分)
    mem_addr = str(data.get("memory_address", "")).strip().upper()
    if mem_addr == "0X000002B47C90F000":
        total_score += 40
        score_details.append({
            "item": "检查 memory_address 定位是否精准并避开诱饵",
            "score": 40, "max_score": 40, "passed": True,
            "reason": "成功定位具有最多碎片的正确内存块 0x000002B47C90F000，且没有掉入诱饵陷阱"
        })
    elif mem_addr == "0X000001FA88000000":
        # 掉入了 Decoy 陷阱：找到了 F 最多的块，但没验证这个块是不是属于前面的 archetype
        total_score += 10
        score_details.append({
            "item": "检查 memory_address 定位是否精准并避开诱饵",
            "score": 10, "max_score": 40, "passed": False,
            "reason": "错误！定位到了包含大量碎片的诱饵块 0x000001FA88000000，但在多表关联时未验证它的 ArchID 是否一致！"
        })
    else:
        score_details.append({
            "item": "检查 memory_address 定位是否精准并避开诱饵",
            "score": 0, "max_score": 40, "passed": False,
            "reason": f"内存地址定位完全错误，实际提取值为: '{mem_addr}'"
        })

    # Ensure total limits
    total_score = max(0, min(100, total_score))
    
    # Output to workplace_score.json
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
