from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import warnings

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import httpx
from openai import AzureOpenAI

from nanoclaw.task_normalizer import normalize_task_file


warnings.filterwarnings("ignore", message="Unverified HTTPS request")

PERSONA_FILE = REPO_ROOT / "doc" / "persona_500.jsonl"
CODE_BLOCK_PATTERN = re.compile(r"```(\w+)?\n(tasks/[^\n]+)\n(.*?)```", re.DOTALL)


def build_client() -> AzureOpenAI:
    api_key = os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    missing = [
        name
        for name, value in (
            ("AZURE_OPENAI_API_KEY or OPENAI_API_KEY", api_key),
            ("AZURE_OPENAI_API_VERSION", api_version),
            ("AZURE_OPENAI_ENDPOINT", azure_endpoint),
        )
        if not value
    ]
    if missing:
        raise RuntimeError(
            "Missing Azure OpenAI configuration: " + ", ".join(missing)
        )

    custom_http_client = httpx.Client(
        verify=False,
        timeout=httpx.Timeout(6000.0, connect=15.0),
    )
    return AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=azure_endpoint,
        http_client=custom_http_client,
    )


def model_name() -> str:
    model = os.getenv("AZURE_OPENAI_DEPLOYMENT") or os.getenv("AZURE_OPENAI_MODEL")
    if not model:
        raise RuntimeError(
            "Missing Azure deployment/model name. Set AZURE_OPENAI_DEPLOYMENT or AZURE_OPENAI_MODEL."
        )
    return model


def init_directories(task_id: str) -> None:
    for path in (
        REPO_ROOT / "tasks" / "prompts",
        REPO_ROOT / "tasks" / task_id,
        REPO_ROOT / "assets" / task_id,
    ):
        path.mkdir(parents=True, exist_ok=True)


def generate_task_for_persona(
    task_id: str,
    persona_data: dict[str, object],
    *,
    client: AzureOpenAI,
    max_retries: int = 3,
) -> str:
    system_prompt = """你是一个顶级的 AI Agent 评测架构师、编剧与全栈工程师。
你深知最高级的 Agent 不需要复杂的封装 API，而是能直接利用底层的系统原语（如 Bash 脚本、Python 编程、文件系统操作）来解决复杂问题。

当前环境说明：
1. 你的目标是：从给定 PERSONA 种子中获取灵感，从零开始为编号 `{task_id}` 生成一套考验底层逻辑推理与代码编写能力的 nanoclaw 任务。
2. Agent 可直接使用文件操作与命令执行工具，自主读写文件、编写脚本、运行 Python/Bash。
3. nanoclaw 的运行语义是：`assets/{task_id}/` 会被整体复制成一次 run 的工作区根目录。因此最终任务提示词必须引用“运行时工作区内的相对路径”，不能让用户去访问仓库根下的 `assets/{task_id}/...` 路径。

你必须严格按照当前仓库结构产出以下文件：
- `tasks/{task_id}.yaml`
- `tasks/prompts/{task_id}.md`
- `tasks/{task_id}/env_builder.py`
- `tasks/{task_id}/verify_rules.py`
- `tasks/{task_id}/verify_prompt.md`

`tasks/{task_id}.yaml` 必须符合当前 nanoclaw schema，最少包含：

```yaml
tasks/{task_id}.yaml
id: {task_id}
name: <task name>
description: <short description>
prompts:
  - prompts/{task_id}.md
environment:
  asset: {task_id}
skills:
  available:
runtime:
  model: gpt-4o
  mode: interactive
  memory_policy: default
  approval_mode: reject
  max_steps: 50
  temperature: 0.2
```

关键约束：
- `prompts` 必须显式存在，并指向 `prompts/{task_id}.md`。
- `environment.asset` 必须写成 `{task_id}`，不能写成 `assets/{task_id}`。
- 如果没有可用 skill，也要显式写：
  ```yaml
  skills:
    available:
  ```
- `tasks/prompts/{task_id}.md` 中出现的输入输出路径，必须是运行时工作区内的相对路径，例如 `docs/input.csv`、`data/logs/`、`deliverables/report.md`。
- `env_builder.py` 的职责是生成 `assets/{task_id}/` 目录下的初始工作区模板。也就是说，脚本里应该往 `assets/{task_id}/docs/...`、`assets/{task_id}/deliverables/...` 等路径写入文件。
- `env_builder.py` 和 `verify_rules.py` 优先使用 Python 标准库；除非绝对必要，不要依赖 `flask`、`pandas` 等第三方包。
- `env_builder.py` 不能启动长驻服务、监听端口、写死 `/workspace` 或 `/assets` 这类绝对路径。
- `verify_rules.py` 应尽量基于当前工作目录或显式传入的 base dir 做校验，不要写死 `/workspace`，也不要假设运行时仍在仓库根。
- `verify_rules.py` 必须默认以“当前工作目录就是任务运行后的工作区根目录”为前提，也可以支持 `sys.argv[1]` 传入 base dir，但两者都必须指向同一个运行时工作区，而不是仓库里的 `assets/{task_id}`。
- `verify_rules.py` 里不要出现字符串字面量 `assets/{task_id}`、`/workspace`、`/assets`；目标文件应写成诸如 `report.json`、`docs/output.csv`、`deliverables/result.md` 这样的工作区相对路径。
- `verify_rules.py` 最好输出一个结构化 JSON 文件（`verify_result.json` 或 `state.json`），并在其中直接给出布尔断言或 `score` 字段，便于后续批量评测。
- 提示词不能给出解题步骤，只能给用户真实会说的话和清晰的成功标准。

请严格按下面顺序输出，并把每个文件内容包裹在 Markdown 代码块中，代码块第一行必须是完整文件路径。例如：

```python
tasks/{task_id}/env_builder.py
[代码内容]
```

生成要求：
1. `tasks/prompts/{task_id}.md`
   - 必须从用户视角出发。
   - 必须严格贴合 persona 的语气、细节程度与做事风格。
   - 必须只引用运行时工作区里的相对路径。
   - 必须让任务可解、可验证。
2. `tasks/{task_id}.yaml`
   - 必须是当前 nanoclaw 可直接加载的合法 YAML。
3. `tasks/{task_id}/env_builder.py`
   - 必须可直接运行。
   - 运行后在 `assets/{task_id}/` 下生成完整初始工作区文件树。
   - 推荐预先创建 `deliverables/`、`docs/`、`data/` 等目录。
4. `tasks/{task_id}/verify_rules.py`
   - 只负责客观物理状态断言，输出 `verify_result.json` 或 `state.json`。
   - 默认使用工作区相对路径；如需 base dir，请写成 `base_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')` 这种形式。
   - 禁止引用仓库内 `assets/{task_id}` 路径。
5. `tasks/{task_id}/verify_prompt.md`
   - 说明如何结合 `trace.jsonl` 和状态 JSON 为任务打分。
"""

    user_prompt = (
        f"当前任务编号：{task_id}\n\n当前 PERSONA 种子：\n"
        f"{json.dumps(persona_data, ensure_ascii=False, indent=2)}"
    )

    for attempt in range(max_retries):
        try:
            print(f"[{task_id}] 正在请求大模型生成关卡 (尝试 {attempt + 1}/{max_retries})...")
            response = client.chat.completions.create(
                model=model_name(),
                messages=[
                    {"role": "system", "content": system_prompt.replace("{task_id}", task_id)},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as exc:
            print(f"[{task_id}] 第 {attempt + 1} 次请求失败: {exc}")
            if attempt < max_retries - 1:
                sleep_time = 2 ** attempt * 5
                print(f"[{task_id}] 等待 {sleep_time} 秒后重试...")
                time.sleep(sleep_time)
                continue
            print(f"[{task_id}] 达到最大重试次数，放弃生成。")
            raise


def parse_and_save(task_id: str, llm_output: str) -> list[Path]:
    matches = CODE_BLOCK_PATTERN.findall(llm_output)
    if not matches:
        raw_output_path = REPO_ROOT / "tasks" / f"{task_id}_raw_output.txt"
        print(f"[{task_id}] 警告：未能解析到标准格式的文件。原始输出已保存到 {raw_output_path}")
        raw_output_path.write_text(llm_output, encoding="utf-8")
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

    task_yaml_path = REPO_ROOT / "tasks" / f"{task_id}.yaml"
    if task_yaml_path.exists():
        normalize_task_file(task_yaml_path, create_backup=False)
        print(f"[{task_id}] 已规范化任务 YAML: {task_yaml_path.relative_to(REPO_ROOT)}")

    print(
        f"[{task_id}] 成功保存 {len(saved_files)} 个文件:\n  "
        + "\n  ".join(str(path.relative_to(REPO_ROOT)) for path in saved_files)
    )
    return saved_files


def build_assets(task_id: str) -> None:
    builder_path = REPO_ROOT / "tasks" / task_id / "env_builder.py"
    if not builder_path.exists():
        return
    print(f"[{task_id}] 正在执行环境构造脚本生成 assets...")
    subprocess.run([sys.executable, str(builder_path)], cwd=REPO_ROOT, check=True)


def main() -> None:
    if not PERSONA_FILE.exists():
        print(f"找不到文件: {PERSONA_FILE}")
        return

    client = build_client()
    with PERSONA_FILE.open("r", encoding="utf-8") as handle:
        for index, line in enumerate(handle):
            if not line.strip():
                continue

            persona_data = json.loads(line)
            task_id = f"data_{index + 1:02d}"
            init_directories(task_id)

            try:
                llm_output = generate_task_for_persona(task_id, persona_data, client=client)
                parse_and_save(task_id, llm_output)
                build_assets(task_id)
            except Exception as exc:
                print(f"[{task_id}] 最终处理失败跳过: {exc}")

            print("-" * 50)


if __name__ == "__main__":
    main()
