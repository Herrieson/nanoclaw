#!/usr/bin/env python3
import os
import sys
import json
import collections
import httpx
from openai import OpenAI

# ====================================================
# 🔒 强制 API 规范：LLM 语义检测接口 (用于代码产物分析)
# ====================================================
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

# ====================================================
# 主检测逻辑
# ====================================================
def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    details = []
    total_score = 0
    
    # ------------------------------------------------
    # 1. 结构与基础文件存在性校验 (10分)
    # ------------------------------------------------
    processed_dir = os.path.join(workspace, "processed")
    clean_path = os.path.join(processed_dir, "clean_sft.jsonl")
    trash_path = os.path.join(processed_dir, "trash_bin.jsonl")
    
    if os.path.isfile(clean_path):
        details.append({"item": "检查 clean_sft.jsonl 是否存在", "score": 5, "max_score": 5, "passed": True, "reason": "文件已生成"})
        total_score += 5
    else:
        details.append({"item": "检查 clean_sft.jsonl 是否存在", "score": 0, "max_score": 5, "passed": False, "reason": "文件缺失"})
        
    if os.path.isfile(trash_path):
        details.append({"item": "检查 trash_bin.jsonl 是否存在", "score": 5, "max_score": 5, "passed": True, "reason": "文件已生成"})
        total_score += 5
    else:
        details.append({"item": "检查 trash_bin.jsonl 是否存在", "score": 0, "max_score": 5, "passed": False, "reason": "文件缺失"})

    # ------------------------------------------------
    # 2. 利用 LLM 检测 Agent 是否遗留了有效的数据处理脚本 (10分)
    # ------------------------------------------------
    script_found = False
    target_script = ""
    for root, dirs, files in os.walk(workspace):
        if any(ignore in root for ignore in ["sft_export", "configs", "processed"]):
            continue
        for file in files:
            if file.endswith(".py") and file not in ["verify_workplace.py", "env_builder.py"]:
                target_script = os.path.join(root, file)
                script_found = True
                break
        if script_found: break
            
    if script_found:
        try:
            with open(target_script, "r", encoding="utf-8") as f:
                script_content = f.read()
            # 借助大模型分析非结构化的代码语义，判断其是否真正包含了处理数据的核心逻辑
            prompt = "Does this Python script contain logic for reading active config, parsing JSON lines, and filtering text length/toxic words? Answer YES or NO."
            is_valid = llm_judge_content(prompt, script_content[:3000])
            if is_valid:
                details.append({"item": "代码产物有效性检查(LLM)", "score": 10, "max_score": 10, "passed": True, "reason": f"找到了有效的数据处理脚本: {os.path.basename(target_script)}"})
                total_score += 10
            else:
                details.append({"item": "代码产物有效性检查(LLM)", "score": 0, "max_score": 10, "passed": False, "reason": f"大模型判定脚本 {os.path.basename(target_script)} 未包含完整处理逻辑"})
        except Exception as e:
            details.append({"item": "代码产物有效性检查(LLM)", "score": 0, "max_score": 10, "passed": False, "reason": f"读取脚本出错: {str(e)}"})
    else:
         details.append({"item": "代码产物有效性检查(LLM)", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 Agent 编写并保存的 Python 脚本产物"})

    # ------------------------------------------------
    # 3. 构建 Ground Truth (绝对确定性的代码级解析)
    # ------------------------------------------------
    expected_clean = collections.Counter()
    expected_trash = collections.Counter()
    sft_dir = os.path.join(workspace, "sft_export")
    
    active_txt_path = os.path.join(workspace, "configs", "active_version.txt")
    active_words = []
    max_m2h, max_h2m = 1.0, 1.0
    human_aliases, model_aliases = set(), set()
    
    try:
        # 严格按照业务逻辑寻找真实配置
        with open(active_txt_path, "r", encoding="utf-8") as f:
            active_txt = f.read()
        
        active_filename = None
        for line in active_txt.splitlines():
            if line.startswith("ACTIVE_CONFIG="):
                active_filename = line.split("=", 1)[1].strip()
        
        if active_filename:
            config_path = os.path.join(workspace, "configs", active_filename)
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
                
            for item in config_data.get("blacklisted_words", []):
                if not item.get("deprecated", False):  # 忽略废弃词汇
                    active_words.append(item["term"].lower())
                    
            max_m2h = config_data.get("ratio_thresholds", {}).get("max_model_to_human", 999.0)
            max_h2m = config_data.get("ratio_thresholds", {}).get("max_human_to_model", 999.0)
            human_aliases = set(config_data.get("actor_mappings", {}).get("human_aliases", []))
            model_aliases = set(config_data.get("actor_mappings", {}).get("model_aliases", []))
            
    except Exception as e:
        print(f"Ground Truth Config Parsed Error: {e}")
        
    # 动态遍历重组期望结果
    if os.path.exists(sft_dir):
        for root, dirs, files in os.walk(sft_dir):
            for file in files:
                if file.endswith(".jsonl"): # 过滤掉 .bak, .tmp 等非 jsonl 文件
                    filepath = os.path.join(root, file)
                    with open(filepath, "r", encoding="utf-8") as f:
                        for line in f:
                            is_trash = False
                            
                            # 1. 底层字节乱码检查
                            if '\uFFFD' in line or '\x00' in line:
                                is_trash = True
                            else:
                                try:
                                    # 2. JSON 解析能力检查
                                    data_obj = json.loads(line)
                                    human_len = 0
                                    model_len = 0
                                    has_toxic = False
                                    
                                    for item in data_obj.get("data", []):
                                        author = item.get("author", "")
                                        content = item.get("content", "")
                                        content_lower = content.lower()
                                        
                                        # 黑名单词校验
                                        for w in active_words:
                                            if w in content_lower:
                                                has_toxic = True
                                                break
                                                
                                        # 角色长度归属校验
                                        if author in human_aliases:
                                            human_len += len(content)
                                        elif author in model_aliases:
                                            model_len += len(content)
                                            
                                    # 3. 业务规则综合判定
                                    if has_toxic:
                                        is_trash = True
                                    elif human_len == 0 or model_len == 0:
                                        is_trash = True
                                    elif (model_len / human_len) > max_m2h:
                                        is_trash = True
                                    elif (human_len / model_len) > max_h2m:
                                        is_trash = True
                                        
                                except json.JSONDecodeError:
                                    is_trash = True
                                    
                            # 录入原始行，保证原封不动匹配
                            if is_trash:
                                expected_trash[line] += 1
                            else:
                                expected_clean[line] += 1

    # ------------------------------------------------
    # 4. 精确的比对验证函数 (抵御幻觉与篡改)
    # ------------------------------------------------
    def evaluate_file(filepath, expected_counter, max_score):
        if not os.path.exists(filepath):
            return 0, 0, 0, "文件未找到"
        
        agent_counter = collections.Counter()
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    agent_counter[line] += 1
        except Exception as e:
            return 0, 0, 0, f"读取文件异常: {e}"
            
        expected_total = sum(expected_counter.values())
        if expected_total == 0:
            return max_score, 0, 0, "无预期数据"
            
        correct, extra = 0, 0
        for line, count in agent_counter.items():
            if line in expected_counter:
                matched = min(count, expected_counter[line])
                correct += matched
                if count > matched:
                    extra += (count - matched)
            else:
                extra += count # 捏造/篡改的行，严重惩罚
                
        missing = expected_total - correct
        
        # 惩罚计算公式：错加一行扣减比例分数的 50%
        penalty = extra * (max_score / expected_total) * 0.5
        raw_score = max_score * (correct / expected_total) - penalty
        final_score = max(0, min(max_score, round(raw_score)))
        
        reason = f"精准匹配: {correct}/{expected_total}行, 篡改或多出: {extra}行, 遗漏: {missing}行"
        return final_score, correct, extra, reason

    # 执行 Clean 判定 (40分)
    clean_score, c_corr, c_extra, c_reason = evaluate_file(clean_path, expected_clean, 40)
    details.append({
        "item": "严格校验 clean_sft.jsonl 行级数据完整与准确性",
        "score": clean_score,
        "max_score": 40,
        "passed": clean_score == 40,
        "reason": c_reason
    })
    total_score += clean_score

    # 执行 Trash 判定 (40分)
    trash_score, t_corr, t_extra, t_reason = evaluate_file(trash_path, expected_trash, 40)
    details.append({
        "item": "严格校验 trash_bin.jsonl 垃圾箱行级数据捕获率",
        "score": trash_score,
        "max_score": 40,
        "passed": trash_score == 40,
        "reason": t_reason
    })
    total_score += trash_score

    # ------------------------------------------------
    # 5. 输出规范化判决
    # ------------------------------------------------
    result = {
        "total_score": total_score,
        "details": details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
