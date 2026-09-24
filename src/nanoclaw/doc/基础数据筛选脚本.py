from __future__ import annotations

import json
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import warnings


# 【重要调整】因为遇到 429 报错，建议将并发数从 50 调低到 20 或 30
MAX_WORKERS = 20
MAX_RETRIES = 50  # API 遇到 429 时的最大重试次数

CODE_BLOCK_PATTERN = re.compile(r"```(\w+)?\n(tasks/[^\n]+)\n(.*?)```", re.DOTALL)
file_lock = threading.Lock()
# ==========================================

QA_SYSTEM_PROMPT = """你是一个顶尖的 AI 评测数据集质检专家。
你的任务是审查由另一个大模型生成的“Agent 评测任务数据”，并对这批数据的质量进行多维度打分。

我将提供从生成结果中提取出的 5 个文件内容（YAML、用户Prompt、环境构建脚本、客观验证脚本、主观裁判标准）。
请你严格根据以下 4 个维度进行评分（每项 0-10 分）：

1. **环境与任务对齐度 (env_alignment_score)**: 
   - EnvBuilder 是否完美还原了 Prompt 描述的场景？是否埋下了脏数据/陷阱？是否有遗漏文件？
2. **规则探针严密性 (rule_robustness_score)**: 
   - `verify_rules.py` 是否足够鲁棒？是否考虑了 Agent 输出 JSON/文本的格式兼容（大小写、列表vs字典）？它是否坚守了“只采集客观布尔值，不计算最终得分”的原则？
3. **裁判标准合理性 (judge_rationality_score)**: 
   - `verify_prompt.md` 是否合理结合了客观状态和行为轨迹？有没有惩罚作弊/幻觉的机制？
4. **剧本沉浸与可解性 (persona_solvability_score)**: 
   - Prompt 是否有扮演好角色且没有剧透解题步骤？任务逻辑上是否可以通过编写 Python 脚本完美解决？

【输出格式】
你必须返回一个合法的 JSON 对象，不要包含多余的 Markdown 标记（不要使用 ```json 包裹），结构如下：
{
  "env_alignment_score": 8,
  "rule_robustness_score": 7,
  "judge_rationality_score": 9,
  "persona_solvability_score": 9,
  "total_score": 33,
  "reasoning": "简要概括你的打分理由，指出具体的优点和致命缺陷（如果有的话）。",
  "recommendation": "keep" // 只有当 total_score >= 32 且没有致命逻辑漏洞时为 "keep"，否则为 "revise" 或 "discard"
}
"""

def get_successfully_processed_indices() -> set[int]:
    """读取已完成的记录，实现断点续传"""
    processed = set()
    if OUTPUT_JSONL.exists():
        with open(OUTPUT_JSONL, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    # 只有当 total_score 存在且不为 -1 (即非报错状态) 时，才算真正处理完成
                    if data.get("qa_result", {}).get("total_score", -1) != -1:
                        if "source_line_index" in data:
                            processed.add(data["source_line_index"])
                except json.JSONDecodeError:
                    continue
    return processed

def extract_files_from_raw(raw_output: str) -> dict:
    matches = CODE_BLOCK_PATTERN.findall(raw_output)
    files = {}
    for _, path, content in matches:
        filename = path.strip().split('/')[-1]
        files[filename] = content.strip()
    return files

def append_qa_result(record: dict) -> None:
    with file_lock:
        with OUTPUT_JSONL.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

def evaluate_task(index: int, raw_line: str) -> None:
    if not raw_line.strip():
        return
    
    try:
        data = json.loads(raw_line)
        raw_output = data.get("raw_output", "")
    except json.JSONDecodeError:
        return

    # 注入数据来源行号，用于断点续传标识
    data["source_line_index"] = index

    files = extract_files_from_raw(raw_output)
    
    if "env_builder.py" not in files or "verify_rules.py" not in files:
        data["qa_result"] = {
            "total_score": 0,
            "reasoning": "文件提取失败，格式严重违规。",
            "recommendation": "discard"
        }
        append_qa_result(data)
        return

    user_content = "【待评测的数据集文件如下】\n\n"
    for path, content in files.items():
        user_content += f"--- {path} ---\n{content}\n\n"

    req_data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": QA_SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ],
        "response_format": {"type": "json_object"}
    }

    # ================= 带有退避机制的重试逻辑 =================
    qa_json = None
    last_error = ""
    
    for attempt in range(MAX_RETRIES):
        try:
            response = (
                model_agent=MODEL_AGENT,
                req_data=req_data,
                sub_account_name=SUB_ACCOUNT_NAME,
                model=MODEL_NAME,
                timeout=120
            )
            
            content = ""
            if isinstance(response, dict):
                content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            else:
                content = str(response)
                
            content = content.replace("```json", "").replace("```", "").strip()
            qa_json = json.loads(content)
            break  # 成功解析，跳出重试循环
            
        except Exception as e:
            last_error = str(e)
            # 捕获限流相关的错误关键字
            if "429" in last_error or "rate_limit" in last_error or "负载已饱和" in last_error:
                sleep_time = (2 ** attempt) * 3  # 指数退避: 3s, 6s, 12s, 24s...
                print(f"[Line {index}] 触发限流，等待 {sleep_time} 秒后进行第 {attempt + 1}/{MAX_RETRIES} 次重试...")
                time.sleep(sleep_time)
            else:
                # 如果是其他非限流错误（如解析错误），短暂停顿后重试
                time.sleep(2)
                
    # =========================================================

    if qa_json:
        data["qa_result"] = qa_json
        print(f"完成第 {index} 条审查，评分: {qa_json.get('total_score')}，建议: {qa_json.get('recommendation')}")
    else:
        # 重试耗尽仍然失败
        print(f"[Line {index}] 达到最大重试次数，评估最终失败。原因: {last_error}")
        data["qa_result"] = {
            "total_score": -1,
            "reasoning": f"评测接口多次请求异常: {last_error}",
            "recommendation": "error"
        }

    append_qa_result(data)


def main():
    if not INPUT_JSONL.exists():
        print(f"输入文件不存在: {INPUT_JSONL}")
        return

    if not OUTPUT_JSONL.exists():
        OUTPUT_JSONL.touch()

    # 读取断点记录
    processed_indices = get_successfully_processed_indices()
    print(f"检测到历史记录：已成功处理 {len(processed_indices)} 条数据，将跳过它们执行断点续传。")

    lines = []
    with INPUT_JSONL.open('r', encoding='utf-8') as f:
        lines = f.readlines()

    tasks_to_run = []
    for idx, line in enumerate(lines):
        if idx not in processed_indices:
            tasks_to_run.append((idx, line))

    print(f"开始质检，本次需处理数据: {len(tasks_to_run)} 条 (并发数: {MAX_WORKERS})...")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(evaluate_task, idx, line) for idx, line in tasks_to_run]
        for future in as_completed(futures):
            future.result()

    print(f"\n质检跑批结束！结果保存在: {OUTPUT_JSONL}")

if __name__ == "__main__":
    main()
