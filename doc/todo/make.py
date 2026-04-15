import os
import json
import re
import time
import httpx
import warnings
from openai import AzureOpenAI

# 屏蔽关闭 SSL 校验后产生的大量冗余警告，保持控制台整洁
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

# ================= 配置区 =================
# 强烈建议将 KEY 设为环境变量，或在跑完后重置
PERSONA_FILE = "PERSONA_train_combined_500.jsonl"
# ==========================================

# ================= 核心修复：网络与证书绕过 =================
# 配置一个极度宽容的 HTTP 客户端，强制关闭 SSL 证书校验，穿透企业内网拦截
custom_http_client = httpx.Client(
    verify=False,
    timeout=httpx.Timeout(6000.0, connect=15.0),
    # 如果需要显式代理（如 Clash 或企业指定代理 IP），取消下方注释并修改地址
    # proxy="http://127.0.0.1:7890"
)

# 1. 使用 Azure 专属客户端，并接管底层网络请求
client = AzureOpenAI(
    api_key=API_KEY,
    api_version=API_VERSION,
    azure_endpoint=AZURE_ENDPOINT,
    http_client=custom_http_client
)

def init_directories(task_id):
    """初始化目标目录结构"""
    dirs = [
        f"tasks/prompts",
        f"tasks/{task_id}",
        f"assets/{task_id}"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def generate_task_for_persona(task_id, persona_data, max_retries=3):
    """调用大模型 API 生成数据，包含指数退避的重试机制"""
    system_prompt = """你是一个顶级的 AI Agent 评测架构师、编剧与全栈工程师。
你深知最高级的 Agent 不需要复杂的封装 API，而是能直接利用底层的系统原语（如 Bash 脚本、Python 编程、文件系统操作）来解决复杂问题。

当前环境说明：
1. 你的终极目标是：从给定的 PERSONA 种子中获取灵感，从零开始为一个编号为 `{task_id}` 的数据集生成一套考验“底层逻辑推理与代码编写能力”的关卡任务。
2. Agent 拥有以下基础工具，且具备极强的自主编写、安装和执行 Python/Bash 代码的能力：
   - 文件操作: `read`, `write`, `edit`, `apply_patch`, `grep`, `find`, `ls`
   - 命令执行: `exec`, `process`
综上，你可以认为模型可以执行绝大多数任务，**不要在提示词中过于明显给出任务步骤、解决方案、需要使用的工具等提示。**

注意：必须严格按照当前仓库结构约定组织产物。统一采用以下路径约定：
- 任务 YAML：`tasks/{task_id}.yaml`
- 任务 Prompt：`tasks/prompts/{task_id}.md`
- 环境生成脚本：`tasks/{task_id}/env_builder.py`
- 规则校验脚本：`tasks/{task_id}/verify_rules.py`
- LLM 评分 Prompt：`tasks/{task_id}/verify_prompt.md`

请严格按照以下步骤顺序执行。为了方便自动化脚本提取产物，**请务必将每个文件的内容包裹在 Markdown 代码块中，并在代码块的第一行写明完整的文件路径**（例如 ````python\ntasks/{task_id}/env_builder.py\n[代码内容]\n````）：

**1. 种子延展与宏观设计 (Persona Driven Architecture)**
- 读取提供的 PERSONA 任务种子，构思一个高度写实、有陷阱、且必须通过多步系统操作（例如：查找日志分析线索 -> 编写爬虫获取信息 -> 本地处理数据 -> 发送伪造请求）才能解决的评测剧本。
- 生成一个任务指令，保存为 `tasks/prompts/{task_id}.md`。指令必须从用户角度出发，不必要给出步骤、提示、教程等任何帮助，但确保任务是可解可验证的。
- 必须确保你的问题风格与你所选择的那条persona数据描述的人设完全相同，说话语气、做事风格要严格遵守他的风格，如一个专业程序员可能给出详细的术语、步骤(但依旧存在难点)，一个政府公务员可能只会给出模糊的指示，非常慌乱，需要让模型自己在工作空间寻找线索。
- 同时生成 `tasks/{task_id}.yaml`，包含该任务的基础元数据（如 `id`, `name`, `environment.asset` 等配置项）。

**2. 底层环境与基础设施伪造 (Infrastructure Mocking Setup)**
- 编写 `tasks/{task_id}/env_builder.py`。
- 此脚本执行后，必须在 `assets/{task_id}/` 目录下生成所有剧情所需的物理文件、数据库或本地网络服务模拟件（不要写到旧版的 workspace 中）。

**3. 混合多维度校验机制 (The Hybrid Judge)**
- 编写 `tasks/{task_id}/verify_rules.py`: 一个轻量级 Python 脚本，只负责断言客观物理状态（例如：检查目标目录下的特定文件是否生成、正则匹配关键内容，或查询本地 Mock 数据库是否收到了预期的请求）。该脚本运行后应输出一个结构化的事实字典 `verify_result.json`（或 `state.json`）。
- 编写 `tasks/{task_id}/verify_prompt.md`: 用于输入给 nanoclaw（LLM裁判）的多维度打分 Prompt。明确评分标准（总分 100 分），并告知裁判结合 Agent 运行生成的 `trace.jsonl` 和上述的状态验证 JSON 进行最终打分。
"""

    user_prompt = f"当前任务编号：{task_id}\n\n当前 PERSONA 种子：\n{json.dumps(persona_data, ensure_ascii=False, indent=2)}"

    for attempt in range(max_retries):
        try:
            print(f"[{task_id}] 正在请求大模型生成关卡 (尝试 {attempt + 1}/{max_retries})...")

            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt.replace("{task_id}", task_id)},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
            )
            return response.choices[0].message.content

        except Exception as e:
            print(f"[{task_id}] 第 {attempt + 1} 次请求失败: {e}")
            if attempt < max_retries - 1:
                sleep_time = 2 ** attempt * 5  # 5s, 10s 退避
                print(f"[{task_id}] 等待 {sleep_time} 秒后重试...")
                time.sleep(sleep_time)
            else:
                print(f"[{task_id}] 达到最大重试次数，放弃生成。")
                raise e


def parse_and_save(task_id, llm_output):
    """利用正则解析 LLM 输出的 Markdown 代码块并保存为文件"""
    pattern = re.compile(r'```(\w+)?\n(tasks/[^\n]+)\n(.*?)```', re.DOTALL)
    matches = pattern.findall(llm_output)

    if not matches:
        print(f"[{task_id}] 警告：未能解析到标准格式的文件。")
        with open(f"tasks/{task_id}_raw_output.txt", "w", encoding="utf-8") as f:
            f.write(llm_output)
        return

    saved_files = []
    for lang, filepath, content in matches:
        filepath = filepath.strip()
        if filepath.startswith("tasks/"):
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content.strip() + "\n")
            saved_files.append(filepath)

    print(f"[{task_id}] 成功保存 {len(saved_files)} 个文件:\n  " + "\n  ".join(saved_files))


def main():
    if not os.path.exists(PERSONA_FILE):
        print(f"找不到文件: {PERSONA_FILE}")
        return

    with open(PERSONA_FILE, 'r', encoding='utf-8') as f:
        for index, line in enumerate(f):
            if not line.strip():
                continue

            persona_data = json.loads(line)
            task_id = f"data_{index + 1:02d}"

            init_directories(task_id)

            try:
                llm_output = generate_task_for_persona(task_id, persona_data)
                parse_and_save(task_id, llm_output)

                # 动态执行环境构造脚本
                builder_path = f"tasks/{task_id}/env_builder.py"
                if os.path.exists(builder_path):
                    print(f"[{task_id}] 正在执行环境构造脚本生成 assets...")
                    os.system(f"python3 {builder_path}")

            except Exception as e:
                print(f"[{task_id}] 最终处理失败跳过: {e}")

            print("-" * 50)


if __name__ == "__main__":
    main()