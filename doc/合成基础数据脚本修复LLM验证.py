from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import warnings

# 内部依赖库 (来自代码一)
import hmwrangler_init
from hmwrangler import hm_aigc

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

# ================= 动态路径计算 =================
SCRIPT_DIR = Path("/home/semtp/notebooks/gemini_0421")
REPO_ROOT = SCRIPT_DIR
# 如果需要支持 nanoclaw_normalizer, 可以将上级目录加入 sys.path
# if str(REPO_ROOT) not in sys.path:
#     sys.path.insert(0, str(REPO_ROOT))
# try:
#     from nanoclaw.task_normalizer import normalize_task_file
# except ImportError:
#     normalize_task_file = None
# ===============================================

# ================= 配置区 =================
MODEL_AGENT = "yunwu"
SUB_ACCOUNT_NAME = "云雾_教育办公_侯宇泰_0401"
MODEL_NAME = "gemini-3-pro-preview"

# 使用 Path 对象进行路径管理 (采用代码二的规范)
PERSONA_FILE = REPO_ROOT / "persona2000.jsonl"
OUTPUT_JSONL_FILE = REPO_ROOT / "all_outputs_for_copy_0421_fix_verifier.jsonl"
MAX_WORKERS = 100  # 最大并行线程数

# 解析大模型输出的正则表达式
CODE_BLOCK_PATTERN = re.compile(r"```(\w+)?\n(tasks/[^\n]+)\n(.*?)```", re.DOTALL)

# 线程锁，用于安全写入 JSONL
file_lock = threading.Lock()
# ==========================================


def init_directories(task_id: str) -> None:
    """初始化目标目录结构 (代码二规范)"""
    for path in (
        REPO_ROOT / "tasks" / "prompts",
        REPO_ROOT / "tasks" / task_id,
        REPO_ROOT / "assets" / task_id,
    ):
        path.mkdir(parents=True, exist_ok=True)


def append_to_jsonl(llm_output: str) -> None:
    """线程安全地将输出追加到 JSONL 文件 (代码一机制)"""
    with file_lock:
        with OUTPUT_JSONL_FILE.open("a", encoding="utf-8") as f:
            record = {"raw_output": llm_output}
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def generate_task_for_persona(task_id: str, persona_data: dict[str, object], max_retries: int = 30) -> str:
    """调用大模型生成任务 (代码二 Prompt + 代码一 API)"""
    
    # 采用代码二极致严格的 System Prompt
    system_prompt = """你是一个顶级的 AI Agent 评测架构师、资深编剧与全栈工程师。
你的目标是：从给定 PERSONA 种子中获取灵感，从零开始为编号 `{task_id}` 生成一套高质量、极具区分度的 nanoclaw Agent 评测任务。

【🔥输出格式要求 —— 极其重要，否则流水线将崩溃🔥】
请严格按顺序输出这 5 个文件，并把每个文件内容包裹在 Markdown 代码块中。
代码块内部的第一行，必须是纯文本的完整相对路径，绝对不能带有任何注释符（如 # 或 //）或多余字符！

正确的输出示例：
```python
tasks/{task_id}/env_builder.py
import os
def build_env():
    pass
```

【核心设计哲学 —— 必须绝对服从】
这套评测任务的质量取决于“各司其职”：
1. User Prompt 必须是纯粹的“剧本演绎”，绝不能剧透解题步骤。
2. verify_rules.py 是“物理探针”，只负责采集客观事实，绝对不能打分。
3. verify_prompt.md 是“终极大语言模型法官”，负责统筹客观结果与 Agent 行为轨迹，给出最终得分。

你需要产出的 5 个文件如下：

### 1. `tasks/{task_id}.yaml`
必须符合 nanoclaw schema，包含 prompt 路径、`asset: {task_id}` 以及基础的 runtime 配置。

### 2. `tasks/prompts/{task_id}.md`（重中之重：剧本演绎）
- **绝对禁止**：出现“1, 2, 3”这样的解题步骤、变量名、预期数值结果，或“你需要生成包含某某字段的JSON”这种程序化指令。
- **必须做到**：完全代入 Persona 的角色！这是一封邮件、一段工单留言或一次口头对话。
- **内容呈现**：用角色的语气交代背景、抱怨问题、提出业务目标。让 Agent 自己去推导需要输出什么格式。提及文件时，只能使用运行时工作区内的相对路径（如 `docs/`，不能有 `assets/`）。
- *反面案例*：“1. 读取 records. 2. 过滤未授权. 3. 输出 summary.json，包含 approved_hours 键。”
- *正面案例*：“上帝啊，那些不守规矩的志愿者把签到表弄得一团糟，文件都在 records 里。帮我查清楚那些不在白名单里却混进来的人，还有，把合格志愿者的总工时给我理出一份正式报告放在 deliverables 目录下，我马上要用！”

### 3. `tasks/{task_id}/env_builder.py`（沙盒构建）
- 使用 Python 标准库生成具有挑战性的初始文件树（包含干扰项、脏数据等）。
- **🚨极其重要🚨**：执行此脚本时，系统的当前工作目录 (cwd) **已经被设定为了 `assets/{task_id}/`**。因此，请直接在代码中使用简单的相对路径（如 `os.makedirs("raw_logs")` 或 `open("data.csv", "w")`）。**绝对不要**在 Python 代码里再写死 `assets/{task_id}/` 这种路径前缀，否则会导致目录树无限嵌套并污染根目录！

### 4. `tasks/{task_id}/verify_rules.py`（客观探针 - 零容错）
- **职责**：只做“物理世界”的检查。检查文件是否存在、格式是否合规、关键数值/字符串是否绝对匹配。
- **绝对禁止**：计算 `score` 字段！绝对不允许出现 0.5、1.0 这种分数。
- **必须输出**：请务必使用 Python 原生的文件操作（如 `json.dump`），将客观状态写入到一个名为 `state.json` 的**真实物理文件**中，不能仅仅使用 print 打印。
- *输出格式示例*：
  ```json
  {
    "deliverables_exist": true,
    "json_format_valid": true,
    "math_calculated_perfectly": false,
    "unapproved_names_found": true
  }
  ```
- 默认工作区为当前目录，或通过 `sys.argv[1]` 传入。

### 5. `tasks/{task_id}/verify_prompt.md`（LLM 法官标准）
- 这是给 LLM 裁判看的 Prompt。必须明确指示 LLM 裁判如何结合 `state.json`（客观探针结果）和 `trace.jsonl`（Agent 运行轨迹）来计算最终的 0-100 分。
- **必须定义计分权重**：例如“客观结果分（60分） + 行为轨迹分（40分）”。
- **客观结果评判**：教 LLM 裁判如何读取 `state.json` 中的布尔值。如果有 false，扣除相应的客观分。
- **行为轨迹评判（查 trace.jsonl）**：教 LLM 裁判检查 Agent 是否使用了合适的工具（如 Python 脚本优于低效 bash）、是否出现了幻觉（捏造数据）、在终端的输出是否符合角色的互动规范。如果没有写代码而是靠猜，直接扣光轨迹分。
"""

    user_prompt = (
        f"当前任务编号：{task_id}\n\n当前 PERSONA 种子：\n"
        f"{json.dumps(persona_data, ensure_ascii=False, indent=2)}"
    )

    req_data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt.replace("{task_id}", task_id)},
            {"role": "user", "content": user_prompt}
        ]
    }

    # 采用代码一的请求逻辑
    for attempt in range(max_retries):
        try:
            response = hm_aigc.aigc_managed(
                model_agent=MODEL_AGENT,
                req_data=req_data,
                sub_account_name=SUB_ACCOUNT_NAME,
                model=MODEL_NAME,
                timeout=300
            )
            content = ""
            if isinstance(response, dict):
                if "choices" in response and len(response["choices"]) > 0:
                    content = response["choices"][0]["message"]["content"]
                elif "content" in response:
                    content = response["content"]
                else:
                    content = json.dumps(response, ensure_ascii=False)
            else:
                content = str(response)
            return content
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt * 5)
            else:
                print(f"[{task_id}] 达到最大重试次数，放弃生成。")
                raise e
    return ""


def parse_and_save(task_id: str, llm_output: str) -> list[Path]:
    """解析并落盘 (代码二规范的 pathlib 鲁棒性)"""
    matches = CODE_BLOCK_PATTERN.findall(llm_output)
    if not matches:
        print(f"[{task_id}] 警告：未能解析到标准格式的文件。")
        return []

    saved_files: list[Path] = []
    for _, relative_path, content in matches:
        relative_path = relative_path.strip()
        if not relative_path.startswith("tasks/"):
            continue
        destination = REPO_ROOT / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content.strip() + "\n", encoding="utf-8")
        saved_files.append(destination)

    # 如果有 normalizer 可以放开下面的注释
    # task_yaml_path = REPO_ROOT / "tasks" / f"{task_id}.yaml"
    # if task_yaml_path.exists() and normalize_task_file:
    #     normalize_task_file(task_yaml_path, create_backup=False)

    return saved_files


def build_assets(task_id: str) -> None:
    """安全执行环境构建脚本 (强制沙盒机制)"""
    builder_path = REPO_ROOT / "tasks" / task_id / "env_builder.py"
    # 定义目标资产目录
    asset_dir = REPO_ROOT / "assets" / task_id 
    
    if not builder_path.exists():
        return
    
    # 确保运行前目录一定存在
    asset_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # 【核心修复】将 cwd (当前工作目录) 直接设定为 asset_dir。
        # 这样脚本里的任何相对路径操作，都会被死死限制在 assets/{task_id}/ 里面！
        subprocess.run([sys.executable, str(builder_path)], cwd=asset_dir, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"[{task_id}] 环境构造脚本执行失败: {e.stderr.decode('utf-8', errors='ignore')}")


def process_single_task(index: int, line: str) -> None:
    """单个任务的处理逻辑，供线程池调用 (代码一机制)"""
    if not line.strip():
        return

    persona_data = json.loads(line)
    task_id = f"data_{index + 1:02d}"

    # --- 断点续传检查 ---
    checkpoint_file = REPO_ROOT / "tasks" / f"{task_id}.yaml"
    if checkpoint_file.exists():
        print(f"[{task_id}] 检测到已存在，跳过。")
        return

    print(f"[{task_id}] 开始处理...")
    init_directories(task_id)

    try:
        # 1. 生成大模型结果
        llm_output = generate_task_for_persona(task_id, persona_data)
        
        # 2. 线程安全保存 Raw 数据到独立日志 (代码一特性)
        append_to_jsonl(llm_output)

        # 3. 解析落盘
        saved_files = parse_and_save(task_id, llm_output)
        
        # 4. 执行生成资产
        if saved_files:
            build_assets(task_id)
            
        print(f"[{task_id}] 处理完成，保存了 {len(saved_files)} 个文件。")
    except Exception as e:
        print(f"[{task_id}] 运行出错: {e}")


def main() -> None:
    """多线程并发入口"""
    if not PERSONA_FILE.exists():
        print(f"找不到文件: {PERSONA_FILE}")
        return

    # 初始化 RAW 日志文件
    if not OUTPUT_JSONL_FILE.exists():
        OUTPUT_JSONL_FILE.touch()

    tasks_to_run = []
    with PERSONA_FILE.open('r', encoding='utf-8') as f:
        for index, line in enumerate(f):
            tasks_to_run.append((index, line))

    print(f"总计任务数: {len(tasks_to_run)}，开始执行多线程处理 (Workers: {MAX_WORKERS})...")

    # 使用线程池执行 (代码一特性)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_single_task, idx, line) for idx, line in tasks_to_run]
        
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"线程池捕获到异常: {e}")

    print(f"\n全部处理尝试完毕！输出已保存至: {OUTPUT_JSONL_FILE}")


if __name__ == "__main__":
    main()
