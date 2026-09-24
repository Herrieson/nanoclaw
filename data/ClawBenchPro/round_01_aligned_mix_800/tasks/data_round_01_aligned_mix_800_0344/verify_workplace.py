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

def extract_all_values(d):
    """递归提取 JSON 中的所有叶子节点值，用于严格的数据对比"""
    values = []
    if isinstance(d, dict):
        for v in d.values():
            values.extend(extract_all_values(v))
    elif isinstance(d, list):
        for v in d:
            values.extend(extract_all_values(v))
    elif d is not None:
        values.append(str(d))
    return values

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0
    
    deliv_dir = os.path.join(workspace, "deliverables")
    dir_exists = os.path.isdir(deliv_dir)
    
    # [1] 检查交付目录是否存在 (10分)
    if dir_exists:
        details.append({"item": "检查交付目录 deliverables 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "deliverables 目录已创建"})
        total_score += 10
    else:
        details.append({"item": "检查交付目录 deliverables 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "deliverables 目录不存在"})
    
    # 查找目标 JSON
    json_path = None
    if dir_exists:
        for f in os.listdir(deliv_dir):
            if f.endswith(".json"):
                json_path = os.path.join(deliv_dir, f)
                break
                
    json_data = None
    json_valid = False
    
    # [2] 检查 JSON 格式与合法性 (15分)
    if json_path:
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            json_valid = True
            details.append({"item": "检查 JSON 文件是否存在且格式合法", "score": 15, "max_score": 15, "passed": True, "reason": f"成功加载并解析 JSON 文件: {os.path.basename(json_path)}"})
            total_score += 15
        except Exception as e:
            details.append({"item": "检查 JSON 文件是否存在且格式合法", "score": 0, "max_score": 15, "passed": False, "reason": f"解析 JSON 失败: {str(e)}"})
    else:
        details.append({"item": "检查 JSON 文件是否存在且格式合法", "score": 0, "max_score": 15, "passed": False, "reason": "目录中未找到 JSON 后缀的文件"})
        
    # [3-5] 数据深度与业务逻辑验证
    if json_valid and json_data is not None:
        values = extract_all_values(json_data)
        values_str = [v.upper() for v in values]
        
        # [3] 检查品牌色 (30分) - 必须精确命中3个加密解析出的 HEX 码
        c1 = any("#1A5276" in v for v in values_str)
        c2 = any("#F1C40F" in v for v in values_str)
        c3 = any("#333333" in v for v in values_str)
        
        if c1 and c2 and c3:
            details.append({"item": "检查加密品牌调色盘解析结果", "score": 30, "max_score": 30, "passed": True, "reason": "精准提取了 Primary, Secondary 和 Text 的 HEX 色值"})
            total_score += 30
        elif c1 or c2 or c3:
            details.append({"item": "检查加密品牌调色盘解析结果", "score": 10, "max_score": 30, "passed": False, "reason": "部分 HEX 色值缺失，可能未能完全解析品牌调色盘"})
            total_score += 10
        else:
            details.append({"item": "检查加密品牌调色盘解析结果", "score": 0, "max_score": 30, "passed": False, "reason": "未在结构化数据中找到目标 HEX 色值"})

        # [4] 陷阱排雷：检查是否混入 Veda 的废弃数据 (15分)
        has_noise = False
        for v in values_str:
            if "#FFFFFF" in v or "#000000" in v or "VEDA" in v:
                has_noise = True
                break
        if has_noise:
            details.append({"item": "检查是否误入 Veda 数据陷阱", "score": 0, "max_score": 15, "passed": False, "reason": "触发零容忍条件：JSON 中混入了归档项目 Veda 的废弃信息"})
        else:
            details.append({"item": "检查是否误入 Veda 数据陷阱", "score": 15, "max_score": 15, "passed": True, "reason": "数据纯净，成功屏蔽了 Veda 相关的干扰源"})
            total_score += 15
            
        # [5] 纯净度与语义审查：检查大段语音转文字录音的解析结果 (30分)
        all_text = " ".join(values)
        prompt_text = (
            "Does the following extracted text containing the exact core mission statement "
            "('Empowering digital communities through intuitive scalable web solutions.') "
            "AND completely omit conversational noise/transcription artifacts "
            "(such as 'cow', 'driving', 'vibe', 'Client:')?"
        )
        if llm_judge_content(prompt_text, all_text):
            details.append({"item": "大模型校验 - 使命宣言的纯净度与语义完整性", "score": 30, "max_score": 30, "passed": True, "reason": "大模型判定使命宣言被准确提取，且剔除了所有的无关转录对话"})
            total_score += 30
        else:
            details.append({"item": "大模型校验 - 使命宣言的纯净度与语义完整性", "score": 0, "max_score": 30, "passed": False, "reason": "大模型判定使命宣言未能完整提取，或 Agent 图省事直接拷贝了包含口语（如 cow, vibe）的原始噪音转录文本"})
            
    else:
        # 级联失败
        details.append({"item": "检查加密品牌调色盘解析结果", "score": 0, "max_score": 30, "passed": False, "reason": "由于前置 JSON 文件缺失或损坏，无法验证"})
        details.append({"item": "检查是否误入 Veda 数据陷阱", "score": 0, "max_score": 15, "passed": False, "reason": "由于前置 JSON 文件缺失或损坏，无法验证"})
        details.append({"item": "大模型校验 - 使命宣言的纯净度与语义完整性", "score": 0, "max_score": 30, "passed": False, "reason": "由于前置 JSON 文件缺失或损坏，无法验证"})

    result = {
        "total_score": total_score,
        "details": details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
