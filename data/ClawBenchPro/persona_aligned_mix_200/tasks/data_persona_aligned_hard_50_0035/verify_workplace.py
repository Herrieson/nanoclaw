#!/usr/bin/env python3
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
    此函数为检测非结构化文本的统一接口
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
    
    total_score = 0
    details = []

    # 1. 基础目录与文件存在性 (10分)
    target_file = os.path.join(workspace, "hotfix", "target_fix.json")
    if os.path.exists(target_file):
        total_score += 10
        details.append({"item": "检查结果目录及文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 hotfix/target_fix.json 存在"})
    else:
        details.append({"item": "检查结果目录及文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 hotfix/target_fix.json"})

    # 2. JSON Schema合法性 (10分)
    json_data = None
    if os.path.exists(target_file):
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            total_score += 10
            details.append({"item": "文件是否为合法JSON结构", "score": 10, "max_score": 10, "passed": True, "reason": "原生代码 json.load 解析成功"})
        except Exception as e:
            details.append({"item": "文件是否为合法JSON结构", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
    else:
        details.append({"item": "文件是否为合法JSON结构", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在，无法进行 Schema 解析"})

    # 3. 字段完整性及多余字段/幻觉检查 (10分)
    extra_info_collected = ""
    if json_data and isinstance(json_data, dict):
        keys = list(json_data.keys())
        has_req = "supernode_id" in keys and "leak_address" in keys
        extra_keys = [k for k in keys if k not in ["supernode_id", "leak_address"]]
        
        if has_req and not extra_keys:
            total_score += 10
            details.append({"item": "字段完整性及纯净度", "score": 10, "max_score": 10, "passed": True, "reason": "恰好仅包含要求的两个必填字段，没有伪造冗余数据"})
        elif has_req and extra_keys:
            details.append({"item": "字段完整性及纯净度", "score": 5, "max_score": 10, "passed": False, "reason": f"包含必填字段，但有额外未被要求的冗余字段: {extra_keys}"})
            for k in extra_keys:
                extra_info_collected += f"{k}: {json_data[k]}\n"
        else:
            details.append({"item": "字段完整性及纯净度", "score": 0, "max_score": 10, "passed": False, "reason": "缺少必填字段 supernode_id 或 leak_address"})
    else:
        details.append({"item": "字段完整性及纯净度", "score": 0, "max_score": 10, "passed": False, "reason": "未解析出合法的JSON对象字典结构"})

    # 4. 定位真凶数据 - supernode_id 精确提取 (30分)
    if json_data and isinstance(json_data, dict) and "supernode_id" in json_data:
        val = str(json_data["supernode_id"]).strip()
        if val == "V_0xdead_66666":
            total_score += 30
            details.append({"item": "提取关键数据 supernode_id", "score": 30, "max_score": 30, "passed": True, "reason": "成功提取出正确的导致崩溃的超级节点ID"})
        elif val == "V_0xbeef_11111":
            details.append({"item": "提取关键数据 supernode_id", "score": 0, "max_score": 30, "passed": False, "reason": "【严厉扣分】踩中陷阱 Decoy 1: 找到了溢出任务，但未验证内存流的 RefChain 是否形成真实闭环！"})
        elif val == "V_0xcafe_22222":
            details.append({"item": "提取关键数据 supernode_id", "score": 0, "max_score": 30, "passed": False, "reason": "【严厉扣分】踩中陷阱 Decoy 2: 找到了真实闭环，但未验证其在 Coordinator 中的状态是否引发了 FRAG_SPLIT_OVERFLOW！"})
        else:
            details.append({"item": "提取关键数据 supernode_id", "score": 0, "max_score": 30, "passed": False, "reason": f"提供的值 {val} 不正确，逻辑未贯通或产生幻觉。"})
    else:
        details.append({"item": "提取关键数据 supernode_id", "score": 0, "max_score": 30, "passed": False, "reason": "缺少该必填字段"})

    # 5. 提取精确泄漏地址 - leak_address 精确提取 (30分)
    if json_data and isinstance(json_data, dict) and "leak_address" in json_data:
        val = str(json_data["leak_address"]).strip()
        if val == "0x7fa1b2c3d4e5":
            total_score += 30
            details.append({"item": "提取精确泄漏地址 leak_address", "score": 30, "max_score": 30, "passed": True, "reason": "成功提取出完美闭环的根内存地址"})
        elif val == "0x7f9999999999":
            details.append({"item": "提取精确泄漏地址 leak_address", "score": 0, "max_score": 30, "passed": False, "reason": "【严厉扣分】踩中陷阱 Decoy 2: 提取了常态内存驻留（干扰环）的泄漏地址，并非真正导致集群崩溃的地址。"})
        else:
            details.append({"item": "提取精确泄漏地址 leak_address", "score": 0, "max_score": 30, "passed": False, "reason": f"提供的值 {val} 不正确，未能通过代码解析出正确的指针起始位置。"})
    else:
        details.append({"item": "提取精确泄漏地址 leak_address", "score": 0, "max_score": 30, "passed": False, "reason": "缺少该必填字段"})

    # 6. LLM 检查多余文档与语义一致性 (10分)
    hotfix_dir = os.path.join(workspace, "hotfix")
    if os.path.exists(hotfix_dir):
        # 搜集可能由 Agent 留下的任何多余文本或排查报告
        for f in os.listdir(hotfix_dir):
            if f != "target_fix.json" and os.path.isfile(os.path.join(hotfix_dir, f)):
                try:
                    with open(os.path.join(hotfix_dir, f), "r", encoding="utf-8") as tf:
                        extra_info_collected += f"\nFile {f} content:\n{tf.read(2000)}\n"
                except Exception:
                    pass
    
    if not extra_info_collected.strip():
        total_score += 10
        details.append({"item": "大模型辅助验证：是否有非预期的冗余信息或幻觉", "score": 10, "max_score": 10, "passed": True, "reason": "Agent 严格遵守指令，只输出了指定的 JSON 格式，未自作主张留下冗余文件或幻觉字段，满分。"})
    else:
        prompt = (
            "The user provided extra explanations/files in the workspace while performing a Graph Database incident investigation task.\n"
            "The investigation requires a strict 3-step reasoning logic: \n"
            "1. Finding 'FRAG_SPLIT_OVERFLOW' TaskID in coordinator logs. \n"
            "2. Tracing TaskID to Worker IP via router json routing tables. \n"
            "3. Checking 'RefChain' strings in Worker dump files to ensure the start and end memory addresses identically match (thus forming a real closed loop).\n"
            "Does the following extra content correctly mention or align with this 3-step reasoning without making up irrelevant hallucinations? "
            "If it contains sensible explanations matching the core logic, say YES. If it's pure hallucination, random guesses, complains, or contradicts the logic, say NO."
        )
        passed_llm = llm_judge_content(prompt, extra_info_collected)
        if passed_llm:
            total_score += 10
            details.append({"item": "大模型辅助验证：非预期冗余信息的合理性", "score": 10, "max_score": 10, "passed": True, "reason": "大模型判定附加的报告或字段符合严格的三步排查逻辑，未出现严重幻觉"})
        else:
            details.append({"item": "大模型辅助验证：非预期冗余信息的合理性", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定附加信息包含幻觉乱编，或未能反映出真正的排查原理，视为捏造信息倒扣此项"})

    result = {
        "total_score": total_score,
        "details": details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
