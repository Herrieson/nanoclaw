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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    truth_path = os.path.join(workspace, ".system_config", "truth.json")
    target_path = os.path.join(workspace, "recovery", "target.json")
    
    # 获取 Ground Truth
    try:
        with open(truth_path, "r") as f:
            truth_data = json.load(f)
        expected_rank = truth_data["deadlock_rank"]
        expected_coords = truth_data["coordinates"]
    except Exception as e:
        print(f"Failed to load Ground Truth: {e}")
        sys.exit(1)

    # 1. 检查目标文件是否存在 (10分)
    target_exists = os.path.exists(target_path)
    if target_exists:
        score_details.append({"item": "检查产物文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 recovery/target.json 已成功生成。"})
        total_score += 10
    else:
        score_details.append({"item": "检查产物文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 recovery/target.json，Agent 失败。"})
        # 核心文件缺失，直接写入0分并退出
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": score_details}, f, indent=2, ensure_ascii=False)
        return

    # 读取文件内容供后续判断
    with open(target_path, "r") as f:
        target_content = f.read()

    # 2. 检查 JSON 格式合法性与 Schema 匹配度 (20分)
    parsed_json = None
    try:
        parsed_json = json.loads(target_content)
        if "rank_id" in parsed_json and "coordinates" in parsed_json:
            score_details.append({"item": "JSON格式与Schema合法性", "score": 20, "max_score": 20, "passed": True, "reason": "成功解析为合法的 JSON，且包含所需的键名。"})
            total_score += 20
        else:
            score_details.append({"item": "JSON格式与Schema合法性", "score": 5, "max_score": 20, "passed": False, "reason": "是合法 JSON，但缺失 rank_id 或 coordinates 键。"})
            total_score += 5
    except json.JSONDecodeError:
        score_details.append({"item": "JSON格式与Schema合法性", "score": 0, "max_score": 20, "passed": False, "reason": "文件包含非标准 JSON（可能混入了 Markdown 标记或其他文本），无法被 json.loads 解析。"})

    # 3. 数据精准核对: Rank ID (30分)
    if parsed_json and parsed_json.get("rank_id") == expected_rank:
        score_details.append({"item": "死锁 Rank ID 提取准确度", "score": 30, "max_score": 30, "passed": True, "reason": f"成功找出引发死锁的 Rank ID: {expected_rank}。"})
        total_score += 30
    else:
        actual_rank = parsed_json.get("rank_id") if parsed_json else "N/A"
        score_details.append({"item": "死锁 Rank ID 提取准确度", "score": 0, "max_score": 30, "passed": False, "reason": f"Rank ID 错误。期望: {expected_rank}, 实际: {actual_rank}。严重扣分。"})

    # 4. 数据精准核对: 坐标系匹配 (30分)
    if parsed_json and isinstance(parsed_json.get("coordinates"), list):
        actual_coords = parsed_json.get("coordinates")
        if actual_coords == expected_coords:
            score_details.append({"item": "NaN 溢出点多维坐标提取", "score": 30, "max_score": 30, "passed": True, "reason": f"四维坐标系完全匹配: {expected_coords}。"})
            total_score += 30
        else:
            score_details.append({"item": "NaN 溢出点多维坐标提取", "score": 0, "max_score": 30, "passed": False, "reason": f"坐标系错误或顺序不当。期望: {expected_coords}, 实际: {actual_coords}。这通常意味着 Agent 产生了严重幻觉或未能正确调用分析引擎。"})
    else:
        score_details.append({"item": "NaN 溢出点多维坐标提取", "score": 0, "max_score": 30, "passed": False, "reason": "无法读取坐标数组。"})

    # 5. 语言合规检查 (10分) - 考察是否有教科书式的废话或多余的道歉
    prompt = (
        "Check if the following file content strictly only contains a JSON object or JSON string. "
        "The user specifically demanded: '别跟我写什么一二三四的分析步骤，也别用教科书式的废话安慰我'. "
        "Are there any conversational text, apologies, analytical steps, or extra non-JSON explanations included? "
        "Answer 'YES' if the file is PERFECTLY CLEAN (only JSON without conversational fluff), and 'NO' if it contains ANY extra fluff."
    )
    is_clean = llm_judge_content(prompt, target_content)
    if is_clean:
        score_details.append({"item": "交付物纯粹度检查 (LLM判断)", "score": 10, "max_score": 10, "passed": True, "reason": "文件纯粹且无冗余的安抚或步骤说明，符合工程师的急迫业务要求。"})
        total_score += 10
    else:
        score_details.append({"item": "交付物纯粹度检查 (LLM判断)", "score": 0, "max_score": 10, "passed": False, "reason": "包含了业务人员明确禁止的安抚语句、分析步骤说明等废话。"})

    # 写入最终成绩单
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
