import os
import sys
import json
import httpx
from openai import OpenAI

# ---------------------------------------------------------
# 环境与 API 配置
# ---------------------------------------------------------
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 强制关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """
    统一的 LLM 语义检测接口
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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    submission_dir = os.path.join(workspace, "submission")
    final_portfolio_path = os.path.join(submission_dir, "final_portfolio.json")

    total_score = 0
    details = []

    json_data = None

    # =========================================================
    # Check 1: 确定性探针 - 检查文件存在性与 JSON Schema 合法性 (20分)
    # =========================================================
    if not os.path.exists(final_portfolio_path):
        details.append({
            "item": "检查目标文件是否存在", 
            "score": 0, 
            "max_score": 20, 
            "passed": False, 
            "reason": f"未找到文件 {final_portfolio_path}"
        })
    else:
        try:
            with open(final_portfolio_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            details.append({
                "item": "检查目标文件是否存在与格式合法", 
                "score": 20, 
                "max_score": 20, 
                "passed": True, 
                "reason": "文件存在且是合法的 JSON 格式"
            })
            total_score += 20
        except json.JSONDecodeError:
            details.append({
                "item": "检查目标文件是否存在与格式合法", 
                "score": 5, 
                "max_score": 20, 
                "passed": False, 
                "reason": "文件存在，但格式非合法 JSON，解析失败"
            })
            total_score += 5

    # =========================================================
    # Check 2: 确定性探针 - 检查违禁草稿过滤准确性 (30分)
    # 严格杜绝混入焦虑情绪、TODO、以及西语作品
    # =========================================================
    if json_data is not None:
        json_str = json.dumps(json_data, ensure_ascii=False).lower()
        forbidden_keywords = ["el sol", "writer's block", "anxiety", "todo", "nervous"]
        found_forbidden = [kw for kw in forbidden_keywords if kw in json_str]
        
        if found_forbidden:
            details.append({
                "item": "检查是否精准剔除了违规草稿", 
                "score": 0, 
                "max_score": 30, 
                "passed": False, 
                "reason": f"过滤失败，发现违规关键词残留: {found_forbidden}"
            })
        else:
            details.append({
                "item": "检查是否精准剔除了违规草稿", 
                "score": 30, 
                "max_score": 30, 
                "passed": True, 
                "reason": "成功剔除西语作品及含有焦虑/未完成标记的草稿，无幻觉注入"
            })
            total_score += 30
    else:
        details.append({"item": "检查是否精准剔除了违规草稿", "score": 0, "max_score": 30, "passed": False, "reason": "前置解析失败，无法验证数据"})

    # =========================================================
    # Check 3: 确定性探针 - 检查有效诗歌保留完整度 (30分)
    # 必须提取出正确解密后的内容
    # =========================================================
    if json_data is not None:
        required_keywords = ["a sunny day", "nature's peace", "bright", "quiet view"]
        missing_required = [kw for kw in required_keywords if kw not in json_str]
        
        if missing_required:
            details.append({
                "item": "检查最终合规诗歌数据的留存", 
                "score": 0, 
                "max_score": 30, 
                "passed": False, 
                "reason": f"缺失关键的合法诗歌内容节点: {missing_required}"
            })
        else:
            details.append({
                "item": "检查最终合规诗歌数据的留存", 
                "score": 30, 
                "max_score": 30, 
                "passed": True, 
                "reason": "完全包含 poem_a 和 poem_e 的标题及正文，数据无遗漏"
            })
            total_score += 30
    else:
        details.append({"item": "检查最终合规诗歌数据的留存", "score": 0, "max_score": 30, "passed": False, "reason": "前置解析失败，无法验证数据"})

    # =========================================================
    # Check 4: LLM 混合探针 - 检查语义结构化清晰度与数学计算 (20分)
    # 不依赖写死的正则，评估 Agent 编排的 JSON 结构是否直观，以及行数计算是否体现
    # =========================================================
    if json_data is not None:
        with open(final_portfolio_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        prompt = (
            "Analyze the following JSON content which represents a poetry portfolio submission. "
            "1. Does it clearly distinguish the 'Title' and the 'Text' for the selected poems? "
            "2. Does it explicitly include a total line count calculation representing the sum of the lines of the selected poems (should be somewhere around 8 to 10)? "
            "Only answer 'YES' if BOTH the visual JSON schema makes sense and the explicit line count is included."
        )
        llm_passed = llm_judge_content(prompt, file_content)
        
        if llm_passed:
            details.append({
                "item": "利用大模型检查JSON语义及行数汇总", 
                "score": 20, 
                "max_score": 20, 
                "passed": True, 
                "reason": "大模型判定结构清晰，且包含了正确的总行数汇总字段"
            })
            total_score += 20
        else:
            # 降维退化检查：如果大模型觉得结构不好，但代码检测到疑似的行数 (8 或 10)
            if "8" in json_str or "10" in json_str:
                details.append({
                    "item": "利用大模型检查JSON语义及行数汇总", 
                    "score": 10, 
                    "max_score": 20, 
                    "passed": False, 
                    "reason": "大模型判定结构语义不佳，但通过硬编码检测到可能的行数值(8或10)，给予部分得分"
                })
                total_score += 10
            else:
                details.append({
                    "item": "利用大模型检查JSON语义及行数汇总", 
                    "score": 0, 
                    "max_score": 20, 
                    "passed": False, 
                    "reason": "大模型判定不符合要求，且未找到合理的汇总行数计算结果"
                })
    else:
        details.append({"item": "利用大模型检查JSON语义及行数汇总", "score": 0, "max_score": 20, "passed": False, "reason": "前置解析失败，无法验证数据"})

    # 结果回写
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score, 
            "details": details
        }, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
