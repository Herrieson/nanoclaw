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
    """使用大模型检测不可预见的非结构化内容及复杂的语义匹配"""
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

def find_target_number(data, target=15, tolerance=1e-3):
    """在反序列化的 JSON 对象中递归寻找特定的浮点数值"""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (int, float)) and abs(value - target) < tolerance:
                return True
            if find_target_number(value, target, tolerance):
                return True
    elif isinstance(data, list):
        for item in data:
            if find_target_number(item, target, tolerance):
                return True
    return False

def check_board_list_presence(data):
    """
    检查JSON结构中是否包含这4个可用木板的精准数据维度。
    由于Agent的字段命名(keys)可能各不相同，我们抽取所有数字，以集合/列表长度特征来验证。
    """
    # 期望的4块板子的体积 (或包含其长宽高的数值组合)
    # 1. 2, 6, 48
    # 2. 2, 4, 36
    # 3. 1.5, 8, 96
    # 4. 1, 6, 24
    
    # 只要判断它是否包含了这4个特有维度即可。
    # 为防止Agent把数据转换成了字符串 "2x6x48"，我们在LLM验证步骤中提供二次保障
    # 这里的代码验证重点在于：JSON里不能包含非预期的脏数据（如 10x60 或者 Pine 的数据）
    str_dump = json.dumps(data)
    # 检查是否误入了Warped的板子（10x60 -> 10, 60）
    if "10" in str_dump and "60" in str_dump:
        return False, "包含了被判定为Warped的木板数据(1x10x60)"
    # 检查是否误入了Pine的板子 (96，但这跟第三块板子96冲突，我们查Red Oak 72)
    if "72" in str_dump:
         return False, "包含了非White Oak或Red Oak的木板数据(72)"
         
    return True, "未发现明显的杂质数据"

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "project_planning", "usable_oak_report.json")
    
    score_details = []
    total_score = 0
    
    # 1. 检查目标目录与文件是否存在 (20分)
    if os.path.exists(report_path):
        score_details.append({"item": "检查目标文件是否存在", "score": 20, "max_score": 20, "passed": True, "reason": f"{report_path} 文件存在"})
        total_score += 20
    else:
        score_details.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 20, "passed": False, "reason": "文件 project_planning/usable_oak_report.json 不存在"})
        
        # 提前终止并输出
        result = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 2. 检查 JSON 格式合法性 (20分)
    json_data = None
    with open(report_path, "r", encoding="utf-8") as f:
        file_content = f.read()
        try:
            json_data = json.loads(file_content)
            score_details.append({"item": "检查 JSON 格式合法性", "score": 20, "max_score": 20, "passed": True, "reason": "文件是合法的 JSON 格式"})
            total_score += 20
        except json.JSONDecodeError:
            score_details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 20, "passed": False, "reason": "文件无法解析为合法的 JSON"})
            
            result = {"total_score": total_score, "details": score_details}
            with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
                json.dump(result, f, indent=2)
            return

    # 3. 代码精准验证：总板英尺数(Board Feet)计算正确性 (30分)
    # 正确答案为: 4 + 2 + 8 + 1 = 15
    if find_target_number(json_data, 15):
        score_details.append({"item": "验证总板英尺(Total Board Feet)", "score": 30, "max_score": 30, "passed": True, "reason": "成功在JSON中精准提取到数值 15 (或 15.0)"})
        total_score += 30
    else:
        score_details.append({"item": "验证总板英尺(Total Board Feet)", "score": 0, "max_score": 30, "passed": False, "reason": "JSON中缺少正确的总数 15，计算错误或字段缺失"})

    # 4. 代码结构排错 + 大模型语义验证：具体木板清单 (30分)
    # 第一步代码排错：确保没有包含 Red Oak 或 Warped 的木板
    clean, msg = check_board_list_presence(json_data)
    if not clean:
        score_details.append({"item": "验证清单数据的纯净度与准确性", "score": 0, "max_score": 30, "passed": False, "reason": f"代码检测失败: {msg}"})
    else:
        # 第二步大模型检查：确保包含这4个特定维度的板材
        prompt = """
        Examine the following JSON document representing a lumber report.
        Does the report explicitly contain a list showing exactly these 4 specific usable White Oak boards (dimensions can be shown as separate thickness/width/length fields or combined strings):
        - 2 x 6 x 48
        - 2 x 4 x 36
        - 1.5 x 8 x 96
        - 1 x 6 x 24
        It must contain ONLY these 4 boards, without missing any or adding extra ones.
        Answer 'YES' if it matches exactly, otherwise 'NO'.
        """
        is_correct_list = llm_judge_content(prompt, file_content)
        if is_correct_list:
            score_details.append({"item": "验证清单数据的纯净度与准确性", "score": 30, "max_score": 30, "passed": True, "reason": "大模型判定木板清单内容完整且匹配正确维度的 4 块板子"})
            total_score += 30
        else:
            score_details.append({"item": "验证清单数据的纯净度与准确性", "score": 0, "max_score": 30, "passed": False, "reason": "大模型判定木板清单存在缺失、冗余或格式含混不清"})

    # 最终输出
    result = {
        "total_score": total_score,
        "details": score_details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
