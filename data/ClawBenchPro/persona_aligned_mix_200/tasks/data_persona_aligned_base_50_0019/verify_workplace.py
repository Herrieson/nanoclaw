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

def verify_target(workspace):
    score = 0
    details = []

    # 1. 检查目标目录是否存在 (10 分)
    fix_list_dir = os.path.join(workspace, "fix_list")
    if os.path.isdir(fix_list_dir):
        score += 10
        details.append({"item": "检查 fix_list 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录 fix_list 成功创建"})
    else:
        details.append({"item": "检查 fix_list 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录 fix_list 不存在"})

    # 2. 检查结果文件是否存在 (20 分)
    target_file = os.path.join(workspace, "fix_list", "target.json")
    if os.path.isfile(target_file):
        score += 20
        details.append({"item": "检查 target.json 文件是否存在", "score": 20, "max_score": 20, "passed": True, "reason": "文件 target.json 存在"})
        
        # 3. 检查 JSON 格式是否合法 (20 分)
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            score += 20
            details.append({"item": "检查 target.json 格式是否合法", "score": 20, "max_score": 20, "passed": True, "reason": "JSON 格式完全合法且可解析"})
            
            if isinstance(data, dict):
                keys = list(data.keys())
                
                # 4. 检查字段完整性及防止作弊冗余 (10 分)
                if "culprit_asset" in keys:
                    if len(keys) > 1:
                        score += 5
                        details.append({"item": "检查是否仅包含 culprit_asset 字段", "score": 5, "max_score": 10, "passed": False, "reason": "包含 culprit_asset，但捏造/附带了冗余多余的字段，扣除 5 分"})
                    else:
                        score += 10
                        details.append({"item": "检查是否仅包含 culprit_asset 字段", "score": 10, "max_score": 10, "passed": True, "reason": "有且仅有 culprit_asset 字段，非常干净"})
                        
                    # 5. 精准比对最终找到的资产路径值 (40 分)
                    expected_value = "environments/ruins/statue_shattered_piece_04_cinematic.mesh"
                    if data["culprit_asset"] == expected_value:
                        score += 40
                        details.append({"item": "比对 culprit_asset 值是否准确无误", "score": 40, "max_score": 40, "passed": True, "reason": "成功揪出了性能毛刺对应的超高顶点过场静态网格体"})
                    else:
                        details.append({"item": "比对 culprit_asset 值是否准确无误", "score": 0, "max_score": 40, "passed": False, "reason": f"资产路径不匹配。期望: {expected_value}，实际: {data['culprit_asset']}"})
                else:
                    details.append({"item": "检查是否仅包含 culprit_asset 字段", "score": 0, "max_score": 10, "passed": False, "reason": "完全缺失必须的 culprit_asset 键"})
                    details.append({"item": "比对 culprit_asset 值是否准确无误", "score": 0, "max_score": 40, "passed": False, "reason": "因为键缺失，无法验证具体值"})
            else:
                details.append({"item": "检查 JSON 的根节点是否为字典结构", "score": 0, "max_score": 10, "passed": False, "reason": "目标 JSON 不是 Key-Value 格式的字典"})
                details.append({"item": "比对 culprit_asset 值是否准确无误", "score": 0, "max_score": 40, "passed": False, "reason": "数据结构错误，无法获取对应键值"})

        except json.JSONDecodeError as e:
            details.append({"item": "检查 target.json 格式是否合法", "score": 0, "max_score": 20, "passed": False, "reason": f"JSON 解析失败或包含非法字符: {e}"})
            details.append({"item": "检查是否仅包含 culprit_asset 字段", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 无法解析，中止验证"})
            details.append({"item": "比对 culprit_asset 值是否准确无误", "score": 0, "max_score": 40, "passed": False, "reason": "JSON 无法解析，中止验证"})
            
    else:
        details.append({"item": "检查 target.json 文件是否存在", "score": 0, "max_score": 20, "passed": False, "reason": "文件 target.json 未找到"})
        details.append({"item": "检查 target.json 格式是否合法", "score": 0, "max_score": 20, "passed": False, "reason": "文件缺失，中止验证"})
        details.append({"item": "检查是否仅包含 culprit_asset 字段", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失，中止验证"})
        details.append({"item": "比对 culprit_asset 值是否准确无误", "score": 0, "max_score": 40, "passed": False, "reason": "文件缺失，中止验证"})

    # 输出结果记录
    result = {
        "total_score": score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    workspace_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_target(workspace_dir)
