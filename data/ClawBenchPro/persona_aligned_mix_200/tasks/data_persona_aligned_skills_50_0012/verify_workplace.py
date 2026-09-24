import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 强制关闭 SSL 验证以适应内部评测框架
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """大模型统一检测接口，专用于处理非结构化语义的判定"""
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict semantic validation assistant. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[Key String to Evaluate]:\n{file_content}"}
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def flatten_data(y):
    """拉平可能嵌套的 JSON 数据，无论外层是 Dict 还是 List，均展开为平铺路径字典"""
    out = {}
    def flatten(x, name=''):
        if isinstance(x, dict):
            for a in x:
                flatten(x[a], name + a + '_')
        elif isinstance(x, list):
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x
    flatten(y)
    return out

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "report", "conflict_summary.json")
    
    details = []
    total_score = 0
    
    # 1. 物理目录与文件存在性校验 (10分)
    if os.path.exists(report_path):
        details.append({"item": "检查目标结果文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 report/conflict_summary.json 存在"})
        total_score += 10
    else:
        details.append({"item": "检查目标结果文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 report/conflict_summary.json"})
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)
        return

    # 2. JSON 格式与基础规范校验 (10分)
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        details.append({"item": "检查文件是否为合法JSON", "score": 10, "max_score": 10, "passed": True, "reason": "JSON格式合法"})
        total_score += 10
    except Exception as e:
        details.append({"item": "检查文件是否为合法JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {e}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)
        return

    flat_data = flatten_data(data)
    
    # 3. 字段数量校验 (10分) - Prompt 强制要求 exactly three pieces of information
    if len(flat_data) == 3:
        details.append({"item": "检查是否仅包含严格的三个字段", "score": 10, "max_score": 10, "passed": True, "reason": "提取到正好3个字段节点，遵循了指令规范"})
        total_score += 10
    else:
        details.append({"item": "检查是否仅包含严格的三个字段", "score": 0, "max_score": 10, "passed": False, "reason": f"包含 {len(flat_data)} 个节点，未遵循 exactly 3 pieces 的严格要求"})

    # 使用原生代码严谨地抽取值 (禁止用 LLM 去猜测数字)
    lib_key = None
    rogue_key = None
    expected_key = None
    has_distractor = False
    
    for k, v in flat_data.items():
        v_str = str(v).strip().lower()
        if "fmtlib" in v_str or "fmt" == v_str:
            lib_key = k
        if "8.0.1" in v_str:
            rogue_key = k
        if "9.1.0" in v_str:
            expected_key = k
        if "1.74.0" in v_str or "1.82.0" in v_str:
            has_distractor = True

    # 4. 精准值检查与键名语义结合：冲突库 (20分)
    if lib_key:
        prompt = "Does this JSON key semantically represent the concept of a 'library', 'package', 'dependency', or 'conflict name'?"
        if llm_judge_content(prompt, lib_key):
            details.append({"item": "提取并验证冲突库名称(fmtlib)", "score": 20, "max_score": 20, "passed": True, "reason": f"成功提取 fmtlib 且其键名 '{lib_key}' 语义正确"})
            total_score += 20
        else:
            details.append({"item": "提取并验证冲突库名称(fmtlib)", "score": 10, "max_score": 20, "passed": False, "reason": f"虽然包含 fmtlib，但其键名 '{lib_key}' 语义不明朗或被幻觉污染"})
            total_score += 10
    else:
        details.append({"item": "提取并验证冲突库名称(fmtlib)", "score": 0, "max_score": 20, "passed": False, "reason": "未通过代码在任意节点匹配到准确的冲突库名称 fmtlib"})

    # 5. 精准值检查与键名语义结合：流氓版本 (25分)
    if rogue_key:
        prompt = "Does this JSON key semantically represent the concept of a 'rogue', 'wrong', 'loaded', 'actual', or 'error' version that caused a crash?"
        if llm_judge_content(prompt, rogue_key):
            details.append({"item": "提取并验证流氓版本(8.0.1)", "score": 25, "max_score": 25, "passed": True, "reason": f"成功提取 8.0.1 且其键名 '{rogue_key}' 语义正确"})
            total_score += 25
        else:
            details.append({"item": "提取并验证流氓版本(8.0.1)", "score": 10, "max_score": 25, "passed": False, "reason": f"虽然包含 8.0.1，但其键名 '{rogue_key}' 语义不明朗"})
            total_score += 10
    else:
        if has_distractor:
            details.append({"item": "提取并验证流氓版本(8.0.1)", "score": 0, "max_score": 25, "passed": False, "reason": "未找到致命版本 8.0.1，Agent被干扰项(boost 1.82.0)误导产生幻觉"})
        else:
            details.append({"item": "提取并验证流氓版本(8.0.1)", "score": 0, "max_score": 25, "passed": False, "reason": "未能通过原生代码从 JSON 中提取出流氓版本 8.0.1"})

    # 6. 精准值检查与键名语义结合：预期版本 (25分)
    if expected_key:
        prompt = "Does this JSON key semantically represent the concept of an 'expected', 'requested', 'required', or 'original' version?"
        if llm_judge_content(prompt, expected_key):
            details.append({"item": "提取并验证预期版本(9.1.0)", "score": 25, "max_score": 25, "passed": True, "reason": f"成功从云端API调取并提取了预期版本 9.1.0，键名 '{expected_key}' 语义正确"})
            total_score += 25
        else:
            details.append({"item": "提取并验证预期版本(9.1.0)", "score": 10, "max_score": 25, "passed": False, "reason": f"提取到 9.1.0，但键名 '{expected_key}' 语义不明朗"})
            total_score += 10
    else:
        details.append({"item": "提取并验证预期版本(9.1.0)", "score": 0, "max_score": 25, "passed": False, "reason": "未找到预期版本 9.1.0，Agent 可能未正确调用 Nexus GraphQL API 而是凭空捏造"})

    # 输出结果域最终报告
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
