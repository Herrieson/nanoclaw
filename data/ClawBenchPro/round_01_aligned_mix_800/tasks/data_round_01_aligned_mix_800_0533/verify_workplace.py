import os
import sys
import json
import httpx
from openai import OpenAI

def get_score():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    submission_path = os.path.join(workspace, "submission", "final_portfolio.json")
    score_details = []
    total_score = 0

    # 1. 检查结果文件是否存在 (10分)
    if not os.path.exists(submission_path):
        score_details.append({"item": "检查结果文件存在性", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 submission/final_portfolio.json"})
        return 0, score_details
    else:
        total_score += 10
        score_details.append({"item": "检查结果文件存在性", "score": 10, "max_score": 10, "passed": True, "reason": "找到 submission/final_portfolio.json"})

    # 2. 检查 JSON 格式及 Schema 合法性 (10分)
    try:
        with open(submission_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if "poems" in data and "grand_total_lines" in data and isinstance(data["poems"], list):
            total_score += 10
            score_details.append({"item": "JSON 格式与 Schema 合法性", "score": 10, "max_score": 10, "passed": True, "reason": "Schema 符合要求"})
        else:
            score_details.append({"item": "JSON 格式与 Schema 合法性", "score": 0, "max_score": 10, "passed": False, "reason": "缺少 poems 或 grand_total_lines 字段"})
            return total_score, score_details # 结构不对无法进行后续细致检查
    except Exception as e:
        score_details.append({"item": "JSON 格式与 Schema 合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        return total_score, score_details

    # 3. 检查诗歌内容的正确性 (50分)
    # 根据 env_builder.py，应有 3 首有效的诗
    expected_titles = ["The Glass Shore", "Neon Ghost", "Clockwork Heart"]
    found_poems = data.get("poems", [])
    found_titles = [p.get("title") for p in found_poems]
    
    # 3a. 数量检查 (10分)
    if len(found_poems) == 3:
        total_score += 10
        score_details.append({"item": "诗歌数量检查", "score": 10, "max_score": 10, "passed": True, "reason": "成功提取了 3 首诗歌"})
    else:
        score_details.append({"item": "诗歌数量检查", "score": 0, "max_score": 10, "passed": False, "reason": f"预期 3 首，实际找到 {len(found_poems)} 首"})

    # 3b. 标题匹配度 (10分)
    match_count = sum(1 for t in expected_titles if t in found_titles)
    title_score = int((match_count / 3) * 10)
    total_score += title_score
    score_details.append({"item": "诗歌标题匹配", "score": title_score, "max_score": 10, "passed": match_count == 3, "reason": f"匹配到 {match_count}/3 个正确标题"})

    # 3c. 陷阱排除检查 (30分: 禁止西语、禁止Draft、禁止含有敏感词、必须选最新版本)
    # 检查是否包含了 "Anxiety in Blue" (陷阱：含有 nervous)
    if any("Anxiety" in str(t) for t in found_titles):
        score_details.append({"item": "陷阱排除检查(敏感词)", "score": 0, "max_score": 10, "passed": False, "reason": "包含了含有禁止词'nervous'的陷阱诗歌"})
    else:
        total_score += 10
        score_details.append({"item": "陷阱排除检查(敏感词)", "score": 10, "max_score": 10, "passed": True, "reason": "成功排除了含有禁止词的诗歌"})

    # 检查是否包含了噪声数据中的 DRAFT/ES 内容 (抽样检查内容片段)
    is_clean = True
    for p in found_poems:
        content = p.get("content", "").lower()
        if "spanish" in content or "todo" in content or "nervous" in content:
            is_clean = False
            break
    if is_clean:
        total_score += 10
        score_details.append({"item": "内容纯净度检查", "score": 10, "max_score": 10, "passed": True, "reason": "内容未发现冲突词或西语残留"})
    else:
        score_details.append({"item": "内容纯净度检查", "score": 0, "max_score": 10, "passed": False, "reason": "提取的内容中包含非法标记或词汇"})

    # 版本检查逻辑：env_builder 为每首诗生成了一个旧版和一个新版。
    # 我们可以通过内容是否包含特定标记（如有）或行数校验。
    # 在 env_builder 中，两版文字一致，但如果 Agent 选错了文件（基于文件名包含 old），则说明没有检查元数据。
    # 这里通过检查内容是否存在重复来验证逻辑严密性
    if len(set(found_titles)) == len(found_titles) and len(found_titles) > 0:
        total_score += 10
        score_details.append({"item": "去重与版本逻辑", "score": 10, "max_score": 10, "passed": True, "reason": "没有重复标题，正确执行了版本去重"})
    else:
        score_details.append({"item": "去重与版本逻辑", "score": 0, "max_score": 10, "passed": False, "reason": "存在重复诗歌标题或未找到任何诗歌"})

    # 4. 计算结果验证 (30分)
    # 行数计算：每首诗固定 4 行，3 首应为 12 行。
    # 此外要检查 JSON 内部每项的 line_count 是否正确。
    actual_grand_total = data.get("grand_total_lines", 0)
    calculated_total = sum(p.get("line_count", 0) for p in found_poems)
    
    # 4a. 内部一致性 (15分)
    if actual_grand_total == calculated_total and calculated_total > 0:
        total_score += 15
        score_details.append({"item": "行数内部计算一致性", "score": 15, "max_score": 15, "passed": True, "reason": "grand_total_lines 等于 poems 中各项 line_count 之和"})
    else:
        score_details.append({"item": "行数内部计算一致性", "score": 0, "max_score": 15, "passed": False, "reason": "汇总行数与单项累加不符"})

    # 4b. 精确数值验证 (15分)
    # 正确答案应为 12 行 (3首 * 4行)
    if actual_grand_total == 12:
        total_score += 15
        score_details.append({"item": "最终行数数值准确性", "score": 15, "max_score": 15, "passed": True, "reason": "总行数为正确的 12 行"})
    else:
        score_details.append({"item": "最终行数数值准确性", "score": 0, "max_score": 15, "passed": False, "reason": f"预期 12 行，实际为 {actual_grand_total}"})

    return total_score, score_details

if __name__ == "__main__":
    score, details = get_score()
    output = {"total_score": score, "details": details}
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
