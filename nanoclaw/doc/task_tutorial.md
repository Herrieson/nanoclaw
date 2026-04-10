# Task Tutorial

这份文档说明在 `nanoclaw` 里如何从零编写一个任务。

一个任务通常由三部分组成：

- `tasks/<task>.yaml`
- `tasks/prompts/<task>.md`
- `assets/<asset-name>/`

推荐目录结构：

```text
tasks/
  my_task.yaml
  prompts/
    my_task.md

assets/
  my_task_asset/
    MEMORY.md
    active_task.md
    TEAM_STYLE.md
    docs/
      notes.md
    deliverables/
      README.md
```

## 1. 先写任务 YAML

最推荐的写法：

```yaml
id: my_task
name: My Task
description: Short explanation of what this task is testing.

prompts:
  - prompts/my_task.md

environment:
  asset: my_task_asset
  workspace_context_files:
    - TEAM_STYLE.md

skills:
  available:
    - tutorial-brief-writer
    - memory-preference-checker

runtime:
  model: gpt-4o
  mode: interactive
  memory_policy: default
  max_steps: 12
  temperature: 0.1
```

字段说明：

- `id`
  任务唯一标识。运行结果会写到 `results/<id>/`。
- `name`
  任务显示名，主要给人看。
- `description`
  可选说明，方便之后回看任务目的。
- `prompts`
  任务提示词来源。推荐放到单独的 markdown 文件里。
- `environment.asset`
  指定从哪个 `assets/<name>/` 目录复制初始工作区。
- `environment.workspace_context_files`
  指定哪些工作区文件会直接注入 system prompt。
- `skills.available`
  这条任务可用的 skill 集合。模型应从里面挑相关的用，不必全部使用。
- `skills.include`
  可选。强制预激活某个 skill。一般只有你明确要强绑 skill 时才用。
- `skills.auto`
  可选。设为 `true` 时，nanoclaw 会从 `available` 里自动挑一个最匹配的 skill。
- `runtime.model`
  本次任务使用的模型。
- `runtime.mode`
  运行模式，常见是 `interactive`。
- `runtime.memory_policy`
  memory 使用策略。`default` 是普通模式，`strict` 会更强地要求先查 memory，`off` 则不注入 memory policy 指令。
- `runtime.session`
  可选。需要连续多轮任务共用本地 session 时再写。
- `runtime.workspace_context_files`
  可选。运行时级别覆盖 `environment.workspace_context_files`。
- `runtime.max_steps`
  工具调用最大步数。
- `runtime.temperature`
  模型温度。

## 2. 再写 prompt 文件

任务真正的执行要求，应该放在 `tasks/prompts/<task>.md` 里，而不是堆在 YAML 元数据里。

例子：

```md
Read the workspace materials and prepare a short brief.

Requirements:

1. Read `MEMORY.md` and `docs/notes.md`.
2. Write `deliverables/brief.md`.
3. Use these sections:
   - Goal
   - Context
   - Next Step
4. Mention user preferences only if memory supports them.
```

建议：

- 把成功标准写清楚。
- 明确要求读哪些文件、写哪些文件。
- 如果任务依赖 memory，就在 prompt 里直接说“先检查 memory”。
- 尽量让输出可验证，例如固定输出文件路径、固定章节结构。

## 3. 准备 asset 目录

`assets/<asset-name>/` 是任务运行前的初始工作区模板。

例如：

```text
assets/my_task_asset/
  MEMORY.md
  active_task.md
  TEAM_STYLE.md
  docs/
    notes.md
  deliverables/
    README.md
```

这些文件的作用通常是：

- `MEMORY.md`
  放稳定事实、长期偏好、历史结论。
- `active_task.md`
  放当前场景说明。可以有，但真正的任务要求仍建议放在 `prompts/...`。
- `TEAM_STYLE.md`
  放风格规则，适合通过 `workspace_context_files` 注入。
- `docs/...`
  放任务需要读取的材料。
- `deliverables/`
  放模型要生成的输出文件目标目录。

建议：

- 只放任务真正需要的文件，场景越小越容易复现实验。
- 如果任务要求写文件，最好提前建好 `deliverables/`。
- 如果任务跟偏好、历史决策有关，记得把信息放进 `MEMORY.md` 或 `memory/*.md`。

## 4. skill 在任务里怎么配

推荐把候选 skill 放在 `skills.available`：

```yaml
skills:
  available:
    - tutorial-brief-writer
    - memory-preference-checker
```

运行时语义是：

- 这条任务只开放这几个 skill 给模型。
- 模型不需要把它们全都用一遍。
- 它应该先看 skill catalog，再按需读取相关 skill 的 `SKILL.md`。
- nanoclaw 会把这些 skill 镜像到运行工作区的 `.skills/<slug>/SKILL.md`。

所以一个任务完全可以提供多个 skill，但只期望模型使用其中一部分。

## 5. 从零做一个完整样例

假设你要做一个“读取说明并生成简报”的任务。

先建文件：

```text
tasks/my_task.yaml
tasks/prompts/my_task.md
assets/my_task_asset/MEMORY.md
assets/my_task_asset/active_task.md
assets/my_task_asset/TEAM_STYLE.md
assets/my_task_asset/docs/notes.md
assets/my_task_asset/deliverables/README.md
```

`tasks/my_task.yaml`：

```yaml
id: my_task
name: My Task
description: Read notes and produce a short brief.

prompts:
  - prompts/my_task.md

environment:
  asset: my_task_asset
  workspace_context_files:
    - TEAM_STYLE.md

skills:
  available:
    - tutorial-brief-writer
    - memory-preference-checker

runtime:
  model: gpt-4o
  mode: interactive
  memory_policy: default
  max_steps: 12
  temperature: 0.1
```

`tasks/prompts/my_task.md`：

```md
Read the workspace materials and prepare a short brief.

Requirements:

1. Read `MEMORY.md` and `docs/notes.md`.
2. Write `deliverables/brief.md`.
3. Use these sections:
   - Goal
   - Context
   - Next Step
4. Mention user preferences only if memory supports them.
5. In the final answer, confirm the output path.
```

`assets/my_task_asset/MEMORY.md`：

```md
# Memory

- Sam prefers dark mode in editor themes.
- Sam likes short briefs with explicit next steps.
```

`assets/my_task_asset/TEAM_STYLE.md`：

```md
# Team Style

- Keep headings short.
- End with one concrete next step.
```

`assets/my_task_asset/docs/notes.md`：

```md
# Notes

The team needs a short internal brief for tomorrow's walkthrough.
```

## 6. 运行任务

```bash
export OPENAI_API_KEY="<your-key>"
uv run python main.py run-task --task tasks/my_task.yaml
```

如果只是想先看当前仓库有哪些任务和 skill：

```bash
uv run python main.py list-tasks
uv run python main.py list-skills
```

## 7. 跑完后看什么

重点看这些文件：

- `results/my_task/<run-id>/resolved_task.json`
  最终解析后的任务内容。
- `results/my_task/<run-id>/trace.jsonl`
  agent 的工具调用和循环事件。
- `results/my_task/<run-id>/workspace_before/`
  运行前工作区快照。
- `results/my_task/<run-id>/workspace_after/`
  运行后工作区快照。
- `results/my_task/<run-id>/final_answer.md`
  最终回答。

## 8. 推荐做法

- 一个任务只做一件清楚的事。
- prompt 里把成功标准写死，方便后面评估。
- asset 尽量小，不要堆太多无关文件。
- 优先使用 `skills.available`，不要默认把 skill 都做成强制预激活。
- 如果任务本身是教程或实验，尽量让输出文件路径和结构固定。
