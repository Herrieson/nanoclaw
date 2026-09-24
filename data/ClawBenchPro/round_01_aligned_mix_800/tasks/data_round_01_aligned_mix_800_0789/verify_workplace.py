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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_path = os.path.join(workspace, "deliverables")
    
    score = 0
    details = []
    
    # 1. 检查目标目录结构 (10分)
    has_dir = os.path.isdir(deliverables_path)
    if has_dir:
        score += 10
        details.append({"item": "检查交付物目录", "score": 10, "max_score": 10, "passed": True, "reason": "deliverables 目录已成功创建。"})
    else:
        details.append({"item": "检查交付物目录", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 deliverables 目录。"})
        
    # 2. 检查目录内的文件及读取内容 (10分)
    file_content = ""
    if has_dir:
        files = [f for f in os.listdir(deliverables_path) if os.path.isfile(os.path.join(deliverables_path, f))]
        if files:
            score += 10
            details.append({"item": "检查交付物文件", "score": 10, "max_score": 10, "passed": True, "reason": f"在 deliverables 目录中找到文件 {files}。"})
            for f in files:
                try:
                    with open(os.path.join(deliverables_path, f), "r", encoding="utf-8") as file:
                        file_content += file.read() + "\n"
                except Exception as e:
                    pass
        else:
            details.append({"item": "检查交付物文件", "score": 0, "max_score": 10, "passed": False, "reason": "deliverables 目录存在但是为空。"})
    else:
        details.append({"item": "检查交付物文件", "score": 0, "max_score": 10, "passed": False, "reason": "无法检查文件，因为目录不存在。"})
        
    # 如果没有生成文件内容，后续 LLM 校验全部 0 分
    if not file_content.strip():
        for item, ms in [("Stark客户匹配", 15), ("Wayne客户匹配", 15), ("Acme客户匹配", 15), ("佣金精确计算", 25), ("文书语气与剔除干扰项", 10)]:
            details.append({"item": item, "score": 0, "max_score": ms, "passed": False, "reason": "由于没有有效内容，无法进行语义评估。"})
    else:
        # 3. Stark 客户设备匹配精确度 (15分)
        p_stark = "Does the content explicitly and correctly assign the machine 'Atlas-Pro' to 'Stark Industries' (or Tony Stark)?"
        if llm_judge_content(p_stark, file_content):
            score += 15
            details.append({"item": "Stark客户匹配", "score": 15, "max_score": 15, "passed": True, "reason": "完美匹配 Stark 需求，选中最廉价合规机型 Atlas-Pro。"})
        else:
            details.append({"item": "Stark客户匹配", "score": 0, "max_score": 15, "passed": False, "reason": "未能将 Stark 匹配至 Atlas-Pro，可能算错要求或匹配了昂贵机型。"})

        # 4. Wayne 客户设备匹配精确度 (15分)
        p_wayne = "Does the content explicitly and correctly assign the machine 'Hermes-Lite' to 'Wayne Enterprises' (or Bruce Wayne)?"
        if llm_judge_content(p_wayne, file_content):
            score += 15
            details.append({"item": "Wayne客户匹配", "score": 15, "max_score": 15, "passed": True, "reason": "完美匹配 Wayne 需求，选中最廉价合规机型 Hermes-Lite。"})
        else:
            details.append({"item": "Wayne客户匹配", "score": 0, "max_score": 15, "passed": False, "reason": "未能将 Wayne 匹配至 Hermes-Lite。"})
            
        # 5. Acme 客户设备匹配精确度 (15分)
        p_acme = "Does the content explicitly and correctly assign the machine 'Vulcan-Heavy' to 'Acme Corp'?"
        if llm_judge_content(p_acme, file_content):
            score += 15
            details.append({"item": "Acme客户匹配", "score": 15, "max_score": 15, "passed": True, "reason": "完美匹配 Acme 需求，选中最廉价合规机型 Vulcan-Heavy。"})
        else:
            details.append({"item": "Acme客户匹配", "score": 0, "max_score": 15, "passed": False, "reason": "未能将 Acme 匹配至 Vulcan-Heavy。"})
            
        # 6. 佣金结算能力 (25分)
        p_comm = "Does the document clearly state that the total potential commission is exactly 32750 (or 32,750)? Answer NO if this exact number is not found."
        if llm_judge_content(p_comm, file_content):
            score += 25
            details.append({"item": "佣金精确计算", "score": 25, "max_score": 25, "passed": True, "reason": "正确汇总出匹配的最优方案总成本，并计算出 5% 佣金为 32,750。"})
        else:
            details.append({"item": "佣金精确计算", "score": 0, "max_score": 25, "passed": False, "reason": "未找到或未能正确算出 32,750 的总佣金。"})
            
        # 7. 文书格式、语气与去除幻觉/干扰测试 (10分)
        p_tone = "Does the document maintain a purely formal tone and intentionally AVOID mentioning any irrelevant items from a grocery list (like 'carbonara', 'cream', 'guanciale', 'pecorino', 'eggs', or 'pepper')?"
        if llm_judge_content(p_tone, file_content):
            score += 10
            details.append({"item": "文书语气与剔除干扰项", "score": 10, "max_score": 10, "passed": True, "reason": "保持了正式的文件撰写语调，且成功剔除了无关的私人笔记干扰项。"})
        else:
            details.append({"item": "文书语气与剔除干扰项", "score": 0, "max_score": 10, "passed": False, "reason": "交付文档包含了不符合正式总结场景的杂乱私人记录（如意面配方），或者未能维持正式基调。"})

    # 输出结果到 JSON
    result = {
        "total_score": score,
        "details": details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
