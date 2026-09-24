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
    deliverables_dir = os.path.join(workspace, "deliverables")
    config_path = os.path.join(deliverables_dir, "aura_config.json")
    
    details = []
    total_score = 0
    
    # 1. 验证 deliverables 目录是否存在 (10 分)
    if os.path.isdir(deliverables_dir):
        details.append({"item": "检查交付物目录 deliverables 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
        total_score += 10
    else:
        details.append({"item": "检查交付物目录 deliverables 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 deliverables 目录"})
        
    # 2. 验证配置文件是否存在且格式正确 (20 分)
    config_data = None
    if os.path.isfile(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
            details.append({"item": "检查 aura_config.json 格式合法性", "score": 20, "max_score": 20, "passed": True, "reason": "JSON 格式合法并成功解析"})
            total_score += 20
        except json.JSONDecodeError:
            details.append({"item": "检查 aura_config.json 格式合法性", "score": 0, "max_score": 20, "passed": False, "reason": "文件存在但不是合法的 JSON 格式"})
    else:
        details.append({"item": "检查 aura_config.json 格式合法性", "score": 0, "max_score": 20, "passed": False, "reason": "未找到 aura_config.json 文件"})

    # 3. 验证结构化数据的内容准确性 (70 分)
    if config_data and isinstance(config_data, dict):
        # 3.1 Primary Color (15分)
        primary_color = config_data.get("primary_color", "")
        if isinstance(primary_color, str) and primary_color.upper() == "#1A5276":
            details.append({"item": "提取 primary_color", "score": 15, "max_score": 15, "passed": True, "reason": "主色调提取完全准确"})
            total_score += 15
        else:
            details.append({"item": "提取 primary_color", "score": 0, "max_score": 15, "passed": False, "reason": f"主色调错误或缺失: {primary_color}"})

        # 3.2 Secondary Color (15分)
        secondary_color = config_data.get("secondary_color", "")
        if isinstance(secondary_color, str) and secondary_color.upper() == "#F1C40F":
            details.append({"item": "提取 secondary_color", "score": 15, "max_score": 15, "passed": True, "reason": "次要色调提取完全准确"})
            total_score += 15
        else:
            details.append({"item": "提取 secondary_color", "score": 0, "max_score": 15, "passed": False, "reason": f"次要色调错误或缺失: {secondary_color}"})

        # 3.3 Text Color (15分)
        text_color = config_data.get("text_color", "")
        if isinstance(text_color, str) and text_color.upper() == "#333333":
            details.append({"item": "提取 text_color", "score": 15, "max_score": 15, "passed": True, "reason": "文本色调提取完全准确"})
            total_score += 15
        else:
            details.append({"item": "提取 text_color", "score": 0, "max_score": 15, "passed": False, "reason": f"文本色调错误或缺失: {text_color}"})

        # 3.4 Mission Statement (25分)
        mission_statement = config_data.get("mission_statement", "")
        expected_statement = "Empowering digital communities through intuitive scalable web solutions."
        if isinstance(mission_statement, str) and mission_statement.strip() == expected_statement:
            details.append({"item": "提取 mission_statement", "score": 25, "max_score": 25, "passed": True, "reason": "Mission Statement 提取完全准确"})
            total_score += 25
        else:
            # 使用 LLM 进行容错判定（如大小写差异、末尾标点丢失，但语义完全一致则给部分分数）
            if isinstance(mission_statement, str) and mission_statement:
                prompt = f"Does the following text perfectly represent this exact core meaning without any extra hallucinations or drastic changes? Expected: '{expected_statement}'"
                is_similar = llm_judge_content(prompt, mission_statement)
                if is_similar:
                    details.append({"item": "提取 mission_statement", "score": 15, "max_score": 25, "passed": True, "reason": "Mission Statement 存在细微差异但语义通过大模型验证(部分得分)"})
                    total_score += 15
                else:
                    details.append({"item": "提取 mission_statement", "score": 0, "max_score": 25, "passed": False, "reason": "Mission Statement 错误、存在幻觉或严重偏差"})
            else:
                details.append({"item": "提取 mission_statement", "score": 0, "max_score": 25, "passed": False, "reason": "Mission Statement 字段缺失"})
    else:
        details.append({"item": "校验数据内容", "score": 0, "max_score": 70, "passed": False, "reason": "JSON无法解析为字典，无法验证具体字段"})
        
    # 汇总写入
    result = {
        "total_score": total_score,
        "details": details
    }
    
    score_file = os.path.join(workspace, "workplace_score.json")
    with open(score_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    verify()
