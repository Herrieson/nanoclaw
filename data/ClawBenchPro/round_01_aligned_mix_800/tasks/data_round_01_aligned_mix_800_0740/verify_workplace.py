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
    target_dir = os.path.join(workspace, "precinct_desk")
    target_file = os.path.join(target_dir, "bolo_summary.json")

    details = []
    total_score = 0

    # 1. 检查目标目录是否存在 (15分)
    if os.path.isdir(target_dir):
        details.append({"item": "检查目标目录是否存在", "score": 15, "max_score": 15, "passed": True, "reason": "precinct_desk 目录存在"})
        total_score += 15
    else:
        details.append({"item": "检查目标目录是否存在", "score": 0, "max_score": 15, "passed": False, "reason": "precinct_desk 目录不存在"})

    # 2. 检查结果文件及格式合法性 (25分)
    json_data = None
    if os.path.isfile(target_file):
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            if isinstance(json_data, dict):
                details.append({"item": "检查文件及格式合法性", "score": 25, "max_score": 25, "passed": True, "reason": "bolo_summary.json 存在且是合法的 JSON 对象"})
                total_score += 25
            else:
                details.append({"item": "检查文件及格式合法性", "score": 10, "max_score": 25, "passed": False, "reason": "bolo_summary.json 存在但不是 JSON 对象 (dict)"})
                total_score += 10
        except Exception as e:
            details.append({"item": "检查文件及格式合法性", "score": 0, "max_score": 25, "passed": False, "reason": f"文件格式非标准 JSON: {e}"})
    else:
        details.append({"item": "检查文件及格式合法性", "score": 0, "max_score": 25, "passed": False, "reason": "bolo_summary.json 文件不存在"})

    # 辅助生成器：扁平化遍历所有 JSON 的 value，用于不限制键名的数据查找
    def extract_values(d):
        if isinstance(d, dict):
            for k, v in d.items():
                yield v
                yield from extract_values(v)
        elif isinstance(d, list):
            for item in d:
                yield item
                yield from extract_values(item)

    # 3. 检查总价值的准确性 ($27000) (30分)
    value_passed = False
    if json_data:
        for val in extract_values(json_data):
            # 将数值型和字符串格式的数字统一转换为浮点数做宽松比较
            try:
                # 处理可能包含 $ 符号的情况
                val_clean = str(val).replace("$", "").replace(",", "").strip()
                if float(val_clean) == 27000:
                    value_passed = True
                    break
            except:
                pass

        if value_passed:
            details.append({"item": "检查总价值金额计算", "score": 30, "max_score": 30, "passed": True, "reason": "成功找到正确的被盗财物总价值 27000"})
            total_score += 30
        else:
            details.append({"item": "检查总价值金额计算", "score": 0, "max_score": 30, "passed": False, "reason": "JSON 中未找到正确的总价值 (27000)"})
    else:
        details.append({"item": "检查总价值金额计算", "score": 0, "max_score": 30, "passed": False, "reason": "无合法 JSON 数据可供检查"})

    # 4. 检查案件号提取正确性 (102 和 104) (30分)
    cases_passed = False
    if json_data:
        target_cases = {"102", "104"}
        for val in extract_values(json_data):
            if isinstance(val, list):
                # 提取列表中的案卷号并转为字符串格式集合进行比较
                found_cases = {str(item).strip() for item in val if str(item).strip()}
                if found_cases == target_cases:
                    cases_passed = True
                    break

        if cases_passed:
            details.append({"item": "检查涉案案件号提取", "score": 30, "max_score": 30, "passed": True, "reason": "成功找到仅包含案卷号 102 和 104 的列表"})
            total_score += 30
        else:
            details.append({"item": "检查涉案案件号提取", "score": 0, "max_score": 30, "passed": False, "reason": "JSON 中未找到准确的涉案案件号列表 (应仅为 102 和 104)"})
    else:
        details.append({"item": "检查涉案案件号提取", "score": 0, "max_score": 30, "passed": False, "reason": "无合法 JSON 数据可供检查"})

    # 写入结果记录文件
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    verify()
