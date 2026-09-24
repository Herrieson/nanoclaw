import os
import sys
import json
import httpx
import math
from openai import OpenAI

# ====================================================================
# [LLM 配置区域]
# 必须使用 OpenAI SDK，从环境变量读取配置，强制关闭 SSL 验证。
# ====================================================================
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """
    此函数为检测非结构化文本的统一接口。
    当 Agent 违反纯 JSON 规定，捏造了自然语言回复时，用于界定是否包含冗余文字。
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

# ====================================================================
# [探针核心逻辑区域]
# 尽可能全面细致的检查最终产物，利用 Python 原生方法保证数据抽取的确定性
# ====================================================================
def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_file = os.path.join(workspace, "report", "culprit.json")
    
    details = []
    total_score = 0
    
    # [Check 1] 检查文件是否存在 (10分)
    if os.path.exists(report_file):
        details.append({"item": "检查结果文件 culprit.json 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件成功创建"})
        total_score += 10
    else:
        details.append({"item": "检查结果文件 culprit.json 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到目标文件"})
        write_score(total_score, details)
        return

    try:
        with open(report_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
    except Exception as e:
        details.append({"item": "读取文件", "score": 0, "max_score": 0, "passed": False, "reason": f"文件读取失败: {e}"})
        write_score(total_score, details)
        return

    # [Check 2] JSON 格式及 Schema 严谨度检验 (20分)
    parsed_json = None
    format_score = 0
    reason_format = ""
    
    try:
        parsed_json = json.loads(content)
        format_score = 20
        reason_format = "纯粹合法的 JSON 格式"
    except json.JSONDecodeError:
        # Agent 可能添加了 Markdown 标识或附言，引发解析失败。调用 LLM 检测并扣除格式分。
        has_extra_text = llm_judge_content(
            "Does the following text contain conversational natural language or markdown backticks around the JSON?", 
            content
        )
        reason_format = "包含不合规的自然语言或Markdown标记，扣除格式分" if has_extra_text else "JSON格式损坏"
        
        # 宽容提取尝试（基于文本切片，不属于模糊匹配数据内容）
        start = content.find('{')
        end = content.rfind('}')
        if start != -1 and end != -1:
            try:
                parsed_json = json.loads(content[start:end+1])
                format_score = 10 # 兜底给一半的分数
                reason_format += "，但成功通过清洗提取出有效结构化数据"
            except json.JSONDecodeError:
                reason_format += "，且提取清洗失败"
        else:
            reason_format += "，完全无法提取有效结构体"

    # 如果此时未能获取有效的 parsed_json，判定核心验证失败，直接返回
    if parsed_json is None:
        details.append({"item": "JSON 格式合法性与清洗", "score": 0, "max_score": 20, "passed": False, "reason": reason_format})
        write_score(total_score, details)
        return

    # 严查作弊与幻觉字段
    allowed_keys = {"ionic_step", "atom_index", "force_magnitude"}
    actual_keys = set(parsed_json.keys())
    
    if not actual_keys.issubset(allowed_keys):
        format_score = max(0, format_score - 10)
        reason_format += f"；【严惩】发现捏造的多余字段: {actual_keys - allowed_keys}"
    elif not allowed_keys.issubset(actual_keys):
        format_score = max(0, format_score - 10)
        reason_format += f"；【扣分】缺少必要的核心字段: {allowed_keys - actual_keys}"
        
    details.append({
        "item": "JSON 格式结构与幻觉严查", 
        "score": format_score, 
        "max_score": 20, 
        "passed": format_score > 0, 
        "reason": reason_format
    })
    total_score += format_score

    # [Check 3] 精准验证致命离子步 (20分)
    ionic_step = parsed_json.get("ionic_step")
    if str(ionic_step).strip() == "14":
        details.append({"item": "验证离子步序号 (ionic_step)", "score": 20, "max_score": 20, "passed": True, "reason": "精准定位致命离子步: 14"})
        total_score += 20
    else:
        details.append({"item": "验证离子步序号 (ionic_step)", "score": 0, "max_score": 20, "passed": False, "reason": f"离子步识别错误，预期: 14，实际: {ionic_step}"})

    # [Check 4] 精准验证异常原子索引 (20分)
    atom_index = parsed_json.get("atom_index")
    if str(atom_index).strip() == "42":
        details.append({"item": "验证异常原子索引 (atom_index)", "score": 20, "max_score": 20, "passed": True, "reason": "精准定位异常原子: 42"})
        total_score += 20
    else:
        details.append({"item": "验证异常原子索引 (atom_index)", "score": 0, "max_score": 20, "passed": False, "reason": f"原子索引错误，预期: 42，实际: {atom_index}"})

    # [Check 5] 数值计算校验: 欧几里得范数绝对值 (30分)
    # Fx = 845.210, Fy = -991.330, Fz = 1502.440 
    # Sqrt = 1988.57770...
    force = parsed_json.get("force_magnitude")
    expected_val = math.sqrt(845.210**2 + (-991.330)**2 + 1502.440**2)
    
    try:
        force_val = float(force)
        # 允许 ±0.2 的误差，用于囊括可能存在的精度截断或取整操作
        if abs(force_val - expected_val) <= 0.2:
            details.append({"item": "验证受力绝对大小 (force_magnitude)", "score": 30, "max_score": 30, "passed": True, "reason": f"物理欧几里得范数计算正确: {force_val}"})
            total_score += 30
        else:
            details.append({"item": "验证受力绝对大小 (force_magnitude)", "score": 0, "max_score": 30, "passed": False, "reason": f"受力计算错误，预期约: {expected_val:.2f}，实际: {force_val}"})
    except (TypeError, ValueError):
        details.append({"item": "验证受力绝对大小 (force_magnitude)", "score": 0, "max_score": 30, "passed": False, "reason": f"提供的值并非有效浮点数: {force}"})

    write_score(total_score, details)

def write_score(total_score, details):
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": details
        }, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    verify()
