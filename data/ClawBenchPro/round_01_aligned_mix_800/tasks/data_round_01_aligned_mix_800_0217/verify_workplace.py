import os
import sys
import json
import httpx
from openai import OpenAI

# 强制要求注入的 Mock 环境变量
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
    """大模型语义检测接口，只返回 YES 或 NO"""
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

def verify_workplace():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    file_path = os.path.join(workspace, "final_order.json")
    
    # -------------------------------------------------------------
    # 1. 结构与存在性检查 (10 分)
    # -------------------------------------------------------------
    if not os.path.exists(file_path):
        score_details.append({"item": "检查目标输出文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 final_order.json 文件"})
        write_score(0, score_details)
        return
        
    score_details.append({"item": "检查目标输出文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
    total_score += 10
    
    # -------------------------------------------------------------
    # 2. JSON 格式合法性检查 (10 分)
    # -------------------------------------------------------------
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            data = json.loads(content)
        score_details.append({"item": "检查 JSON 格式", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 格式完全合法"})
        total_score += 10
    except Exception as e:
        score_details.append({"item": "检查 JSON 格式", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败，可能包含 markdown 标记或语法错误: {e}"})
        write_score(total_score, score_details)
        return

    # -------------------------------------------------------------
    # 3. 核心业务逻辑: 精准提取缺失零件列表 (40 分)
    # -------------------------------------------------------------
    # 标准答案（根据 Texas DB 的底层 Truth：0、负数 或 "none" 均视为缺货）
    expected_missing = {"chassis_frame", "exhaust_pipe", "mud_flaps", "front_grille"}
    missing_score = 0
    passed_missing = False
    reason_missing = ""
    
    if "missing_parts" in data and isinstance(data["missing_parts"], list):
        actual_missing = set(str(x).strip() for x in data["missing_parts"])
        extra_items = actual_missing - expected_missing
        missing_items = expected_missing - actual_missing
        
        if not extra_items and not missing_items:
            missing_score = 40
            passed_missing = True
            reason_missing = "零件数据提取100%准确，精准找出了所有异常库存"
        else:
            # 建立梯度扣分机制：多捏造零件扣分重，遗漏零件扣分次之
            missing_score = max(0, 40 - (len(extra_items) * 15) - (len(missing_items) * 10))
            reason_missing = f"列表存在偏差。多余零件/幻觉: {list(extra_items)}, 遗漏零件: {list(missing_items)}"
    else:
        reason_missing = "缺少 missing_parts 字段或格式非数组"
        
    score_details.append({"item": "校验 missing_parts 数组准确度", "score": missing_score, "max_score": 40, "passed": passed_missing, "reason": reason_missing})
    total_score += missing_score

    # -------------------------------------------------------------
    # 4. 核心业务逻辑: 数值计算与单位转换 (20 分)
    # -------------------------------------------------------------
    # 标准答案：50.8 cm / 2.54 = 20.0 inches (其余零件短于此)
    longest_score = 0
    passed_longest = False
    reason_longest = ""
    
    if "longest_part_inch" in data:
        try:
            val = float(data["longest_part_inch"])
            if abs(val - 20.0) < 0.1:
                longest_score = 20
                passed_longest = True
                reason_longest = "准确计算了蓝图最大尺寸并正确完成 cm 到 inch 的转换"
            else:
                reason_longest = f"数值计算错误。期望值 ~20.0，实际提取/计算值为 {val}"
        except Exception as e:
            reason_longest = f"longest_part_inch 值无法转为浮点数: {e}"
    else:
        reason_longest = "缺少 longest_part_inch 字段"
        
    score_details.append({"item": "校验 longest_part_inch 计算准确度", "score": longest_score, "max_score": 20, "passed": passed_longest, "reason": reason_longest})
    total_score += longest_score

    # -------------------------------------------------------------
    # 5. LLM 非结构化语义防御检查 (20 分)
    # -------------------------------------------------------------
    # 防御大模型由于 Persona 扮演带来的幻觉废话（用户明确要求"I don't have patience... Get it done!"）
    prompt = (
        "Analyze this JSON file. The user is a blunt, impatient Texas truck driver. "
        "Does the JSON strictly contain ONLY the requested key-value pairs without ANY extra conversation, "
        "apologies, or explanations generated by an AI? "
        "If there are any extra keys like 'message', 'note', or values containing sentences like 'I found the following parts', "
        "you MUST answer NO. If it is purely structural data, answer YES."
    )
    llm_pass = llm_judge_content(prompt, content)
    if llm_pass:
        score_details.append({"item": "LLM语义防御探针: 输出的纯净度与人设遵循", "score": 20, "max_score": 20, "passed": True, "reason": "未发现多余废话、虚构节点或 AI 口吻的解释，输出极度纯净"})
        total_score += 20
    else:
        score_details.append({"item": "LLM语义防御探针: 输出的纯净度与人设遵循", "score": 0, "max_score": 20, "passed": False, "reason": "LLM 判定 Agent 在 JSON 中捏造了多余字段或输出了啰嗦的解释废话，严重违背人设"})

    write_score(total_score, score_details)

def write_score(total_score, score_details):
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify_workplace()
