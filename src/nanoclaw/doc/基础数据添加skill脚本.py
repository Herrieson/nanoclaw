
from __future__ import annotations

import json
import re
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import warnings




# 极其复杂的 Meta-Prompt (注意：这里不要用 f-string，避免跟 Python 代码的 {} 冲突)
SYSTEM_PROMPT_TEMPLATE = """你是一名顶级的 AI Agent 评测架构师与全栈工程师。
你的当前任务是：接收一个**已有的**基础 Agent 评测任务（包含配置文件、剧本提示词、环境构建脚本、验证脚本等），对其进行**“工具链（Skill）依赖增强”**。

【⚠️核心原则 —— 绝对不可违反⚠️】
1. **必须是增强，绝不能是重塑**：你必须保留原任务的 Persona（人物设定）、核心背景故事和最终的客观判定条件。你需要做的是在原有的解决路径上“设置障碍”（如将纯文本变为 PDF、将本地知识变为需要搜索的外部知识），迫使 Agent 必须调用特定的 Skill 才能完成任务。如果完全推倒重来，你将被判定为严重失败。
2. **完整输出**：你必须输出改造后的**完整文件内容**，绝不能输出“修改建议”或“差异（Diff）”。新的 `env_builder.py` 必须能够独立运行并构建完整的最新环境。

---

### 【核心机制：什么是 Skill？】
在我们的框架中，一个 Skill 由两个文件组成：
1. `skills/{skill_name}.md`：Skill 的语义说明书。告诉 Agent 这个工具的作用、输入参数格式、输出格式以及排错指南。
2. `skills/{skill_name}.py`：Skill 的物理执行脚本。Agent 通过命令行调用此脚本获取结果。

---

### 【改造策略与 Mock 编写规范】

#### 1. 任务形态降维（基础增强）
- **策略**：将 `env_builder.py` 中原本生成的 `.csv`、`.txt` 等结构化明文文件，改为不可直接读取的格式（如 PDF、图片、音视频的占位文件）。
- **行动**：修改 `env_builder.py`，新增生成对应的基础 Skill（如 `pdf_parser_skill.md` 和 `.py`）。基础 Skill 的 `.py` 脚本可以直接根据文件路径返回预设的写死文本，无需复杂处理。

#### 2. LLM-as-a-Mock（高级增强 - 针对外部查询类工具）
- **策略**：对于“网络搜索”、“数据库查询”、“外部 API”等千变万化的 Skill，纯代码 Mock 会因为参数不匹配导致评测崩溃。你必须在 Skill 的 `.py` 脚本中使用大模型来做智能兜底和参数纠正！
- **🔒 强制 API 规范**：使用 OpenAI SDK，必须从环境变量读取配置，且强制关闭 SSL 验证。你的 Mock 脚本中必须包含类似以下的核心逻辑：

```python
import os
import sys
import json
import httpx
from openai import OpenAI

# 必须约定这三个环境变量
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 必须使用 httpx 关闭 SSL 验证，防止评测环境证书问题
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def smart_mock(user_params):
    # 1. 检查参数，如果参数明显有误，不要直接崩溃，而是返回带有指导意义的错误信息给 Agent
    if not user_params:
        return "Error: Missing required parameters. Please check the skill documentation."
    
    # 2. 调用大模型进行智能 Mock 回复
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "你是一个虚拟的搜索引擎/API。请根据用户的查询，返回逼真的结果。如果查询超出了当前任务的背景事实，请合理地编造或返回查无此信息。"},
                {"role": "user", "content": f"User Query: {user_params}"}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System Error: Connection failed. {str(e)}"
```

#### 3. 特需skil
- **策略**：不要局限于上述两种skill,针对千遍万化的任务需求给出千变万化的skill,但确保你能处理的好。比如用户任务是股票投资辅助，可能有个skill是某种投资算法。这类skill的存在用于测试模型选择skill的能力，以及增加数据丰富度。




#### 3. 陷阱与鲁棒性测试（Adversarial Skill Design）
- 当你决定引入，可能依赖网络、需要账号、付费或存在其它不确定性因素的skill，典型如**复杂查询类** Skill 时（如 Web Search），**你可以但非必须提供至少两个功能相似的 Skill** 让 Agent 选择。
- **陷阱 Skill**：设计一个“看似更好用”但实际上已损坏的 Skill（如 `bing_search_skill`），其 `.py` 脚本始终返回：“Error 402: Payment Required”或“Network Timeout”。
- **可用 Skill**：设计另一个备用 Skill（如 `Google Search_skill`），它使用上述的 LLM-as-a-Mock 逻辑正常工作。
- **目的**：测试 Agent 在遇到工具调用失败时，是否懂得切换工具，而不是陷入死循环。
*(注：基础的 PDF/Excel 读取类工具不需要做陷阱，只对高级查询工具做陷阱处理。)*

---

### 【输出格式要求 —— 极其严格】
请分析传入的原始任务数据，经过思考后，严格按照以下顺序输出所有的 Markdown 代码块。每个代码块第一行为纯文本的相对路径。

你需要输出的文件集合如下（假设原任务编号为 {task_id}）：
1. `tasks/{task_id}.yaml` (需修改：可能需要增加对 Python `openai` 库的依赖)
2. `tasks/prompts/{task_id}.md` (需修改：在原本的话术中，极其自然地暗示数据变成了 PDF，或者需要查阅外部系统，但不能破坏原有语气)
3. `tasks/{task_id}/env_builder.py` (需修改：生成包含障碍的物理环境，完整代码，而非仅是对改造前环境的修改)
4. `tasks/{task_id}/verify_rules.py` (大概率无需大幅修改，维持原有的客观判定)
5. `tasks/{task_id}/verify_prompt.md` (需修改：在轨迹评分 `trace.jsonl` 中，要求裁判检查 Agent 是否正确调用了 Skill，是否陷入了陷阱 Skill 的死循环)
6. `skills/{task_id}/...` (根据你设计的 Skill，输出对应的 `.md` 和 `.py` 文件，可能有多个) 任何生成的 .py Skill 脚本，必须配备同名的 .md 语义说明书，缺一不可。

现在，请接收原始任务数据并开始你的改造：

=== 原始任务数据 ===
{original_task_data_json_or_text}
=== 原始任务结束 ===
"""

def get_processed_indices() -> set[int]:
    """读取已生成的 JSONL 文件，获取已经处理过的 source_line_index 实现断点续传"""
    processed = set()
    if OUTPUT_JSONL_FILE.exists():
        with OUTPUT_JSONL_FILE.open("r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    if "source_line_index" in data:
                        processed.add(data["source_line_index"])
                except json.JSONDecodeError:
                    pass
    return processed

def call_llm_for_enhancement(task_id: str, original_raw_output: str, max_retries: int = 10) -> str:
    """调用大模型进行数据增强"""
    # 注意这里替换占位符时，不要遗漏原有的模板字符串中的内容
    system_prompt = SYSTEM_PROMPT_TEMPLATE.replace("{original_task_data_json_or_text}", original_raw_output).replace("{task_id}", task_id)
    
    req_data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"请对 {task_id} 进行深度增强改造。务必输出所有完整文件，不要省略。"}
        ]
    }

    for attempt in range(max_retries):
        try:
            response = (
                model_agent=MODEL_AGENT,
                req_data=req_data,
                sub_account_name=SUB_ACCOUNT_NAME,
                model=MODEL_NAME,
                timeout=300
            )
            
            # --- 解析 API 返回内容 ---
            content = ""
            if isinstance(response, dict):
                # 兼容 openai 格式的返回
                if "choices" in response and len(response["choices"]) > 0:
                    content = response["choices"][0]["message"]["content"]
                elif "content" in response:
                    content = response["content"]
                elif "error" in response:
                    # 如果 API 明确返回了错误信息，抛出异常以触发重试
                    raise Exception(f"API Error Response: {json.dumps(response['error'])}")
                else:
                    content = json.dumps(response, ensure_ascii=False)
            else:
                content = str(response)
                
            return content
            
        except Exception as e:
            if attempt < max_retries - 1:
                # 打印日志以观察限流情况
                print(f"[{task_id}] 第 {attempt+1} 次尝试失败，准备重试... 原因: {e}")
                # 增加上限控制的退避算法，防止无限挂起
                sleep_time = min(2 ** attempt * 5, 60)
                time.sleep(sleep_time)
            else:
                print(f"[{task_id}] 达到最大重试次数，API 调用失败: {e}")
                raise e
    return ""

def process_single_record(record_str: str, processed_indices: set[int]) -> None:
    """单个记录的处理逻辑"""
    if not record_str.strip():
        return

    try:
        record = json.loads(record_str)
    except json.JSONDecodeError:
        return

    # 1. 核心过滤逻辑：只有 recommendation == 'keep' 的才处理
    qa_result = record.get("qa_result", {})
    if qa_result.get("recommendation") != "keep":
        return

    # 2. 提取基础信息
    source_index = record.get("source_line_index", -1)
    original_raw = record.get("raw_output", "")
    
    # 尝试从 raw_output 提取 task_id (例如 data_45)
    task_id_match = re.search(r"tasks/(data_\d+)\.yaml", original_raw)
    task_id = task_id_match.group(1) if task_id_match else f"unknown_task_{source_index}"

    # 3. 断点续传检查
    if source_index in processed_indices:
        print(f"[{task_id}] 行号 {source_index} 已存在，跳过。")
        return

    print(f"[{task_id}] 开始进行 Skill 增强改造...")

    try:
        # 4. 调用大模型
        enhanced_output = call_llm_for_enhancement(task_id, original_raw)
        
        if not enhanced_output:
            print(f"[{task_id}] 警告：模型未返回有效数据。")
            return

        # 5. 组装新数据并写入文件 (线程安全)
        new_record = {
            "task_id": task_id,
            "source_line_index": source_index,
            "original_scores": qa_result, # 保留之前的打分记录以供参考
            "enhanced_raw_output": enhanced_output
        }

        with file_lock:
            with OUTPUT_JSONL_FILE.open("a", encoding="utf-8") as f:
                f.write(json.dumps(new_record, ensure_ascii=False) + "\n")
                
        print(f"[{task_id}] 增强完成！")

    except Exception as e:
        print(f"[{task_id}] 处理异常: {e}")

def main() -> None:
    if not INPUT_JSONL_FILE.exists():
        print(f"找不到输入文件: {INPUT_JSONL_FILE}")
        return

    # 获取已处理的断点集合
    processed_indices = get_processed_indices()
    print(f"发现 {len(processed_indices)} 条历史记录，已开启断点续传。")

    records_to_process = []
    with INPUT_JSONL_FILE.open('r', encoding='utf-8') as f:
        records_to_process = f.readlines()

    print(f"读取到总计 {len(records_to_process)} 行记录，开始过滤并执行增强...")

    # 使用线程池并发处理
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(process_single_record, line, processed_indices) 
            for line in records_to_process
        ]
        
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"线程池捕获到顶级异常: {e}")

    print(f"\n全部处理尝试完毕！输出已保存至: {OUTPUT_JSONL_FILE}")

if __name__ == "__main__":
    main()
