# NanoClaw 测试任务数据构造最终方案

这份文档是后续批量构造 `nanoclaw` 测试任务数据的总方案。

它回答的不是“单条任务怎么写”，而是更大的问题：
- 我们应该造什么样的数据；
- 数据之间应该如何组织；
- 如何系统地产生近邻样本；
- 如何给同一类场景做难度梯度；
- 如何让 verifier 真正区分模型强弱；
- 如何把一批 task 组织成可持续扩展的 benchmark 库。

定位上：
- `doc/task.txt` = 生成单条 task 的执行模板
- 本文档 = 批量造数据的上层设计原则与标准流程

后续建议的使用顺序：
1. 先读本文件，理解总体方案；
2. 再用 `doc/task.txt` 驱动单条任务落盘；
3. 用本文件中的验收清单和 family/variant/difficulty 规则做质量控制。

--------------------------------------------------

## 1. 我们要造的不是“散题”，而是“任务家族库”

如果把每条 task 都当成完全孤立、完全不同的题去造，会有几个问题：
- 造题成本太高；
- 题目风格不稳定；
- 很难系统比较模型在“相似但不相同”场景下的表现；
- 很难分析模型是不是在机械套用上一题答案；
- 很难控制难度，只能凭感觉说 easy / hard。

因此，最终推荐方案不是“散题池”，而是：

```text
Benchmark Library
└── Scenario Family
    ├── Base World
    ├── Variant A
    │   ├── easy
    │   ├── medium
    │   └── hard
    ├── Variant B
    │   ├── easy
    │   ├── medium
    │   └── hard
    └── Variant C
        ├── easy
        ├── medium
        └── hard
```

也就是把任务组织成三层：

1. `family`：场景家族
2. `variant`：同一家族中的近邻样本
3. `difficulty`：同一 variant 的难度版本

这是后续批量造数据最重要的组织原则。

--------------------------------------------------

## 2. 核心定义：family / variant / difficulty

### 2.1 Family：场景家族
Family 表示一个相对稳定的业务世界。

它通常共享：
- 角色体系
- 目录结构
- 联系人体系
- 文件风格
- 工作流语境
- 常见约束
- 常见陷阱类型

例子：
- `event_ops`：活动执行与应急决策
- `creator_ops`：内容运营与商务协同
- `incident_response`：事故调查与升级响应
- `partner_comms`：对外沟通与联系人选择
- `compliance_review`：合规审核与证据取舍
- `research_synthesis`：研究材料整合与冲突裁决

Family 的作用不是出具体答案，而是定义一个“稳定宇宙”。

### 2.2 Variant：近邻样本
Variant 是同一 family 里的一个具体样本。

所谓近邻样本，指的是：
- workspace 的大部分基础设定可复用；
- 人物、目录、文件类型、工作流相似；
- 但任务目标、关键证据、正确答案、联系人、输出要求中的一个或多个发生变化。

Variant 不应该只是“换个名字”，而应该是“控制变量后的近邻变化”。

### 2.3 Difficulty：难度版本
Difficulty 是在同一个 variant 上，再通过微调以下内容来构造不同难度：
- workspace 的线索暴露程度
- 冲突数量
- 优先级歧义程度
- 交付物 schema 严格程度
- 干扰项密度
- verifier 对过程的要求

也就是说：
- family 解决“如何复用世界”
- variant 解决“如何产生近邻样本”
- difficulty 解决“如何做难度梯度”

--------------------------------------------------

## 3. 为什么“近邻样本”必须成为正式机制

你提出的“近邻样本”非常关键，我建议把它作为正式设计目标，而不是可选优化。

原因如下：

### 3.1 更贴近真实世界
真实环境中，Agent 经常面对的不是完全陌生世界，而是：
- 相同组织
- 相似目录
- 相同联系人体系
- 相同业务语境
- 但任务目标、最新事实或约束发生了变化

这比“每题都完全不同”更真实。

### 3.2 更能测泛化而不是记忆
如果两个样本很近邻，就能测：
- 模型会不会机械复用上一题答案；
- 模型会不会把上题联系人误用到这题；
- 模型会不会记住“场景里一般都是切室内”，却忽略了当前证据；
- 模型是否真的重新读取本题关键文件。

### 3.3 更适合做 controlled evaluation
近邻样本允许你只改变一个因子，比如：
- 联系人变了
- 合同状态变了
- 人数变了
- 时间窗口变了
- 某个旧资料变成了新资料

这样你就能明确知道：
“模型表现变化到底是因为哪一个变量变了。”

### 3.4 更适合批量扩展
一套 family 的 base world 一旦稳定，后续变体生成成本会大幅降低。

--------------------------------------------------

## 4. 近邻样本的三种正式类型

建议把 near-neighbor variant 分成三类，不要混成一锅。

### 4.1 Surface Neighbor（表层近邻）
特征：
- 核心逻辑基本不变
- 正确答案不变
- 主要变化是表面元素

可变化内容：
- 人名
- 品牌名
- 城市
- 日期
- 文件名风格
- 目录名风格
- 语气

用途：
- 测 prompt overfitting
- 测表层鲁棒性
- 防止模型只背一份样例

### 4.2 Logic Neighbor（逻辑近邻）
特征：
- 表面非常像
- 但某个关键证据变化后，正确答案变了

例如同一个 family：
- 变体 A：indoor backup 有效 -> 正确答案 switch
- 变体 B：indoor backup 已失效 -> 正确答案 postpone
- 变体 C：天气恢复正常 -> 正确答案 keep

用途：
- 测模型是否真的读证据
- 测是否会机械迁移上一题答案

这是最重要的一类近邻样本。

### 4.3 Constraint Neighbor（约束近邻）
特征：
- 世界和证据差不多
- 但输出要求、流程要求、收件规则或 schema 变了

例如：
- 一题只要 brief + json
- 另一题还要 escalation note
- 一题要抄送 venue lead
- 另一题要抄送 legal
- 一题 decision JSON 宽松
- 另一题必须写 accepted/rejected/reasons

用途：
- 测执行纪律
- 测格式控制
- 测“相同推理，不同交付要求”的适应性

--------------------------------------------------

## 5. 难度不应该靠“堆文件数”，而应该靠“认知负担结构化增加”

难度不能简单理解成：
- easy = 5 个文件
- hard = 20 个文件

这样很容易变成低质量噪音。

真正好的难度梯度，应该来自下面这些维度的结构化增强。

### 5.1 搜索难度（search complexity）
- easy：关键文件名直白，入口文件提示清楚
- medium：需要先看 README / constraints / guide 才能定位关键文件
- hard：关键文件分散，需多跳搜索和交叉定位

### 5.2 冲突深度（conflict depth）
- easy：单组旧/新冲突
- medium：两组并行冲突
- hard：多组冲突同时存在，且彼此影响

### 5.3 权威歧义度（authority ambiguity）
- easy：新文件明确写着 supersede old notes
- medium：需要根据日期、valid 标记、说明文字推断优先级
- hard：旧文件看起来也很权威，需要结合多个约束文件才能判定谁更高

### 5.4 输出刚性（output rigidity）
- easy：只要最后结论和关键联系人正确
- medium：要求结构化 JSON
- hard：JSON enum + accepted/rejected source audit + 多个 deliverables + 模板洁净约束

### 5.5 干扰密度（trap density）
- easy：1 个旧来源陷阱
- medium：2-3 个并行陷阱
- hard：4+ 个陷阱，并且其中有些是伪权威来源

### 5.6 过程审计强度（process enforcement）
- easy：只审最终文件
- medium：部分检查 trace
- hard：必须检查 trace 是否经过关键旧/新来源，且 rejected source 必须写全

--------------------------------------------------

## 6. 推荐的难度系统：六旋钮模型

我建议不要只写 easy / medium / hard 三个标签，而是给每条样本维护 6 个 difficulty knobs：

1. `search_complexity`: 0-2
2. `conflict_depth`: 0-2
3. `authority_ambiguity`: 0-2
4. `output_rigidity`: 0-2
5. `trap_density`: 0-2
6. `process_enforcement`: 0-2

然后定义：
- 0-3：easy
- 4-7：medium
- 8-10：hard
- 11-12：adversarial

这比人工拍脑袋打难度标签更稳，也更方便后续统计分析。

--------------------------------------------------

## 7. 最推荐的工程结构：Base + Overlay + Variant

这是我认为最适合 NanoClaw 批量造数据的工程方案。

### 7.1 Base World
每个 family 有一个基础底座，包含：
- 稳定目录结构
- 稳定角色体系
- 稳定联系人体系
- 稳定模板与长期资料
- 一部分共享背景文件

例如：
- README
- MEMORY
- active_task
- contacts/README
- 模板文件
- 一些长期不变的组织规则

### 7.2 Overlay
每个具体样本只覆盖少量关键文件：
- 最新天气
- 最新 amendment
- 当前联系人表
- 草稿箱
- 风险约束
- 数据统计快照

Overlay 的作用是：
- 保持家族一致性
- 用最小改动改变样本逻辑

### 7.3 Variant Prompt
在 base + overlay 之上，再定义任务目标和输出格式。

同样的世界底座可以衍生多种任务：
- 做最终决策
- 做 brief
- 审联系人
- 写 escalation
- 做复盘
- 审核别人留下的 draft

这就是最适合批量扩展的结构。

--------------------------------------------------

## 8. 一个完整任务仍然必须由哪些部分组成

统一采用当前仓库结构：

```text
tasks/
  data_xx.yaml
  prompts/
    data_xx.md
  data_xx/
    env_builder.py
    verify.py
    verify_prompt.md
    report.md

assets/
  data_xx/
    ...

skills/
  data-xx-foo/
    SKILL.md
    mock_script.py

results/
  data_xx/
    <run-id>/
      task.yaml
      resolved_task.json
      trace.jsonl
      summary.json
      final_answer.md
      verify_result.json
      workspace/
      workspace_before/
      workspace_after/
```

### 8.1 `tasks/data_xx.yaml`
建议包含：
- `id`
- `name`
- `description`
- `prompts`
- `environment.asset`
- `environment.workspace_context_files`
- `skills.available`（仅当你需要显式控制技能可见集时）
- `runtime.model`
- `runtime.mode`
- `runtime.memory_policy`
- `runtime.max_steps`
- `runtime.temperature`

关于 `skills.available` 的推荐语义，请统一遵守：
- **缺省（不写 `skills.available`）**：保持当前默认技能发现行为；
- **显式空值（例如 `skills:\n  available:`）**：表示零技能，可见 skill 集为空；
- **显式列表**：表示白名单模式，Agent 只能看到列出的 skills。

额外建议增加内部元信息（即使当前 loader 不直接消费，也建议写进 report 或独立 metadata 文件）：
- `family_id`
- `variant_id`
- `difficulty`
- `canonical_decision`
- `required_files_to_read`
- `common_shortcuts`

### 8.2 `tasks/prompts/data_xx.md`
它必须：
- 定义最终目标
- 定义必须产出的文件
- 明确哪些文件不能修改
- 明确必须审查的冲突源
- 明确 JSON schema
- 明确 accepted/rejected source audit 要求
- 明确不允许的 shortcut

### 8.3 `tasks/data_xx/env_builder.py`
它必须：
- 真实生成 `assets/data_xx/`
- 让每个文件都有清晰角色
- 旧资料必须真的像旧资料
- 新资料必须真的有更高优先级标志
- 不允许空文件或纯占位符

### 8.4 `skills/data-xx-*/SKILL.md`
技能的作用是帮助模型：
- 识别哪些来源优先级高
- 识别哪些文件可能是旧资料
- 理解最终交付物结构
- 避免常见错误

### 8.5 `tasks/data_xx/verify.py`
至少检查：
- 文件是否生成
- JSON schema 是否正确
- 联系人 / evidence / rejected source 是否正确
- trace 是否读过关键旧/新来源
- protected file 是否被改动
- final deliverable 是否有模板污染
- 是否存在 shortcut run

### 8.6 `tasks/data_xx/verify_prompt.md`
适合做：
- 文本质量
- 解释质量
- 幻觉检查
- 业务语气检查

### 8.7 `tasks/data_xx/report.md`
必须记录：
- 任务设计目标
- family / variant / difficulty
- 预期错法
- verifier 设计理由
- 实际 run 问题
- hardening 历史

--------------------------------------------------

## 9. prompt 设计原则

### 9.1 区分“用户表层任务”和“隐式约束系统”
高质量 benchmark 不应该把所有评测要求直接塞进用户提示词。

推荐分成三层：
1. **用户表层任务**：真实用户会说的话，短、自然、像真实请求；
2. **场景隐式约束**：放在 README、constraints、模板、联系人说明、旧资料/新资料冲突中；
3. **评分隐式要求**：放在 verifier 中，而不是让用户直接说“请写 accepted_sources”。

也就是说：
- 用户提示词负责表达“我要什么结果”；
- workspace 负责表达“现实环境里有哪些隐式约束”；
- verifier 负责表达“评测系统如何判断你是不是偷懒”。

### 9.2 不要直接泄露正确策略
反例：
- “如果天气不好且室内可用，应优先切室内”

这几乎等于把解题路径告诉模型。

正确做法：
- 定义目标
- 定义约束
- 定义必须审查的冲突源
- 要求 accepted/rejected source 审计
- 让正确结论从证据系统里长出来

### 9.3 必须显式列出冲突源（但不一定由用户口吻直接说出来）
不要只写“请处理冲突”。

更自然的做法是：
- 用户提示词只说真实目标；
- 关键冲突源由 workspace 里的 README、constraints、handoff、template、contact guide 隐式暴露；
- verifier 再检查模型是否真的审查了这些来源。

如果某条任务处于开发/调试期，也可以先在 prompt 中显式列出关键冲突源；
但进入正式 benchmark 版本时，应尽量把这些要求下沉为场景隐式约束。

应该列：
- 必读旧来源
- 必读新来源
- 必读联系人文件
- 必读约束文件

### 9.4 明确列出“不允许的 shortcut”
例如：
- 不要只读最新资料就下结论
- 不要直接复用旧草稿
- 不要把旧签名当当前联系人
- 不要把 rejected source 混进 final evidence
- 不要把模板内容复制进最终交付物

### 9.5 输出 schema 必须写到 verifier 可以直接实现
如果 verifier 最后要机器判断，那 prompt 里的 schema 必须硬。

但在正式 benchmark 版本里，推荐把 schema 的大部分细节下沉到：
- `deliverables/README.md`
- 受保护模板文件
- 约束说明文件
- verifier

用户表层任务只需要自然地提到：
- 需要哪些交付物
- 需要什么业务结果
而不必把所有评测字段直接写成用户口吻。

--------------------------------------------------

## 10. asset 设计原则

### 10.1 每个文件都要有角色，不要纯凑数
文件角色通常属于：
- 正确主证据
- 次级支持证据
- 旧冲突证据
- 误导性来源
- 联系人 / 约束 / 模板文件
- 输出目录说明

### 10.2 旧文件必须真的像“旧文件”
常见手法：
- 旧日期
- 历史签名
- “可能已失效 / 仅供参考”说明
- 被新文件显式 supersede
- 来自更早上下文

### 10.3 新文件必须有权威性标志
例如：
- signed amendment
- current contacts
- valid=true
- updated_at
- generated_at
- “supersedes earlier notes”

### 10.4 噪音必须是“有效噪音”
不要为了显得复杂就堆随机文件。

有效噪音的标准：
- 看起来合理
- 足以诱导 shortcut
- 最终能被更高优先级证据击败

--------------------------------------------------

## 11. verifier 设计原则

### 11.1 先看结构，再看内容，再看过程
推荐顺序：
1. 文件存在
2. JSON schema
3. 关键字段值
4. deliverable 洁净度
5. trace 过程完整性
6. semantic quality

### 11.2 verifier 必须能惩罚 shortcut
坏 verifier 常见问题：
- 只看最终答案
- 不看 trace
- 不看 rejected sources
- 不看模板污染

好的 verifier 必须抓住：
- shortcut run
- schema mismatch
- template residue
- fake reasoning

### 11.3 联系人字段尽量要求纯邮箱
经验已经证明：
- JSON 中纯邮箱更适合机器校验
- 正文里可以保留显示名
- 结构化字段不要混入展示性装饰

### 11.4 规则评分和语义评分要分层
推荐把 100 分拆成三层：

#### A. 结果正确性（30-40 分）
- 决策是否正确
- 联系人是否正确
- 关键输出文件是否存在
- JSON schema 是否合格

#### B. 过程完整性（30-40 分）
- 是否读过关键旧来源
- 是否读过关键新来源
- 是否显式写 accepted/rejected sources
- 是否写 rejection reasons

#### C. 交付质量（20-30 分）
- brief 是否成品化
- 是否有模板污染
- final answer 是否解释清楚冲突
- email 是否符合语气

--------------------------------------------------

## 12. skill 设计原则

### 12.1 skill 的作用是“帮助避坑”，不是“替模型做题”
skill 应帮助模型：
- 识别高优先级来源
- 识别旧资料
- 理解产物结构
- 避开常见错法

不应该：
- 直接暴露最终答案
- 把所有冲突结论直接写死
- 让任务失去探索必要性

### 12.2 skill 可以明确提示常见错法
例如：
- 不要把 legacy signature 当 current contact
- 不要编辑 DO_NOT_EDIT 模板
- 不要把 abandoned draft 当最终邮件

### 12.3 mock_script.py 必须和 asset 真耦合
它应该：
- 从 workspace 文件读状态
- 返回与场景一致的结构化结果
- 与 verifier 逻辑一致

--------------------------------------------------


## 12.5 `skills-family` 与 `no-skills-family` 两条任务线应并行建设

后续 benchmark 库不应只建设一种任务线，而应并行维护两类 family：

### A. `skills-family`
特点：
- 允许并鼓励 task-scoped skills 出现
- 题目的一部分难点来自 skill 使用时机、skill 文档理解、skill 与 workspace 的配合
- 更适合测：
  - 工具使用策略
  - 技能选择
  - 结构化工作流遵循

例子：
- `event_ops` 中依赖 weather / venue / comms skill 的版本
- `creator_ops` 中依赖 topic research / brand safety / report assembly skill 的版本

### B. `no-skills-family`
特点：
- 不依赖 task-scoped skills
- 只用 NanoClaw 核心工具面与底层工作区求解
- 难点来自：
  - grep / find / read / write / edit / exec 级别的底层链路
  - 本地日志/配置/数据/脚本之间的证据归纳
  - accepted / rejected source 的底层审计

更适合测：
- 底层系统操作能力
- 本地脚本编写与辅助分析能力
- 不借助高层 skill 的证据链构建能力

例子：
- 本地 incident triage
- 配置审计与失配定位
- 日志追踪与根因判断
- 小规模本地数据取证

### 并行建设的原因
如果只造 `skills-family`：
- 容易高估模型“脱离技能文档后的真实底层能力”
- 可能把很多成功归因到 skill guidance，而不是模型自己完成的底层归纳

如果只造 `no-skills-family`：
- 又测不到 skill-aware agent 在复杂工具生态下的真实表现
- 也不适合评估技能库本身的设计价值

因此推荐长期维持双轨：
- 一条 `skills-family` 线
- 一条 `no-skills-family` 线

### 推荐比例
第一阶段建议：
- 60% `skills-family`
- 40% `no-skills-family`

如果后续重点研究“Agent 是否真的会做底层工作”，可调整为：
- 50% `skills-family`
- 50% `no-skills-family`

### 两条线共享什么
两条线仍然共享同一个总框架：
- family / variant / difficulty
- near-neighbor generation
- Base + Overlay + Variant Prompt
- trace-aware verifier
- real-run hardening

不同点只是：
- `skills-family` 的难点部分来自 skill-aware execution
- `no-skills-family` 的难点部分来自 raw workspace + core primitives

### 设计建议
对于每个大主题，尽量同时造：
- 一个 `skills-family` 版本
- 一个 `no-skills-family` 版本

这样你就能比较：
- 模型在有 skill guidance 时的表现
- 模型在无 skill guidance 时是否仍能稳住
- benchmark 是否真的在测能力，而不是测提示词扶手

--------------------------------------------------

## 13. 批量造数据的正式生产流程

### 阶段 1：先定义 family，而不是先写单题
建议先定 3-5 个 family，例如：
- `event_ops`
- `creator_ops`
- `partner_comms`
- `incident_response`
- `compliance_review`

### 阶段 2：每个 family 先做一个 gold base sample
每个 family 先做 1 条高质量样例，要求：
- 结构完整
- run 能跑通
- verifier 有区分度
- 有 clear shortcut trap

### 阶段 3：从 gold base sample 扩展 near-neighbor variants
每个 family 下面建议至少扩：
- 2 个 surface neighbors
- 3-5 个 logic neighbors
- 1-3 个 constraint neighbors

### 阶段 4：给每个 variant 做难度版本
建议每个 variant 至少有：
- easy
- medium
- hard

必要时再加：
- adversarial

### 阶段 5：做弱模型与强模型双配置自测
至少：
- 一轮弱模型 smoke test
- 一轮强模型 quality test

要观察：
- 弱模型是否 shortcut
- 强模型是否能完成完整审计
- verifier 是否能拉开差异

### 阶段 6：根据真实 run 做 hardening
任何题第一次跑出来都不算完成。

要根据真实 trace 看：
- 哪些旧来源没被读
- 哪些 shortcut 还能漏过去
- 哪些 schema 仍然太松
- 哪些模板污染还没被拦住

--------------------------------------------------

## 14. 推荐的元数据方案

我非常建议每条 task 维护元数据，哪怕是通过 `report.md` 或单独 `metadata.json` 存。

推荐字段：
- `family_id`
- `variant_id`
- `difficulty`
- `difficulty_knobs`
- `canonical_decision`
- `required_files_to_read`
- `accepted_source_targets`
- `rejected_source_targets`
- `common_shortcuts`
- `expected_failure_modes`
- `verifier_version`

这些字段在批量分析时非常重要。

--------------------------------------------------

## 15. 批量造数据时最容易犯的错误

### 错误 1：任务其实是“读两份最新资料就结束”
症状：
- steps 很少
- 模型不读旧来源
- verifier 仍高分

解决：
- prompt 强制 stale-source audit
- verifier 检查 trace
- JSON 强制写 rejected_sources

### 错误 2：prompt 提前泄露正确策略
解决：
- prompt 只定义目标、约束、冲突源
- 不直接告诉模型哪条路径更优

### 错误 3：schema 太自由
解决：
- enum 化
- 联系人纯邮箱
- source 用路径
- rejection reasons 用 mapping

### 错误 4：模板保护没进入 verifier
解决：
- 同时检查 protected template 原文件未改动
- final deliverable 无模板污染

### 错误 5：skills 存在但不影响解题
解决：
- skill 必须承担关键避坑价值
- 用真实 run 检查读不读 skill 是否影响表现

### 错误 6：只测一个模型
解决：
- 至少弱模型 + 强模型双配置
- 看 verifier 是否真的有区分度

--------------------------------------------------

## 16. 每道题出厂前的验收清单

### 任务结构
- [ ] `tasks/data_xx.yaml` 能被当前 loader 解析
- [ ] `tasks/prompts/data_xx.md` 定义清楚目标与 schema
- [ ] `tasks/data_xx/env_builder.py` 可成功生成 `assets/data_xx/`
- [ ] `tasks/data_xx/verify.py` 可独立运行

### family / variant / difficulty
- [ ] 该题明确属于某个 family
- [ ] 该题明确属于某个 variant 类型（surface / logic / constraint）
- [ ] 该题有 difficulty 标记
- [ ] difficulty knobs 已记录

### 场景质量
- [ ] 至少有 1 组明确旧/新冲突
- [ ] 冲突有客观优先级
- [ ] 至少有 1 个联系人陷阱或操作陷阱
- [ ] 至少有 1 个模板/交付物陷阱

### Prompt 质量
- [ ] 没有直接泄露正确策略
- [ ] 显式要求检查关键冲突源
- [ ] 明确要求 accepted/rejected source 审计
- [ ] JSON schema 足够硬

### Verifier 质量
- [ ] 检查结果正确性
- [ ] 检查过程完整性
- [ ] 检查模板污染
- [ ] 检查 stale-source audit
- [ ] 能区分 shortcut run 和 full-audit run

### 自测质量
- [ ] 至少跑过 1 次弱模型
- [ ] 至少跑过 1 次强模型
- [ ] verifier 对二者有明显区分
- [ ] `report.md` 记录了 hardening 历史

--------------------------------------------------

## 17. 结合 `data_42` 得出的关键经验

`data_42` 暴露出来的经验非常有代表性：

第一版问题：
- prompt 暗示正确策略过强
- 旧冲突源不是必经路径
- verifier 没有惩罚模板残留
- JSON 联系人字段格式不够刚性

hardening 后的正确方向：
- 强制显式检查旧/新来源
- 强制写 accepted/rejected source 审计
- verifier 增加 trace 检查
- verifier 惩罚 template residue
- schema 改硬

这说明：

> 高质量 benchmark 不是一次写出来的，
> 而是通过真实模型运行、查看 trace、发现 shortcut、再持续加固得到的。

--------------------------------------------------

## 18. 最终推荐方案（一句话版）

后续批量造数据时，采用如下正式方案：

1. 用 `family` 组织世界；
2. 用 `variant` 组织近邻样本；
3. 用 `difficulty knobs` 组织难度梯度；
4. 用 `Base + Overlay + Variant Prompt` 组织工程实现；
5. 用 `trace-aware verifier` 抑制 shortcut；
6. 用真实 run + hardening 作为最终质量闭环。

如果要把它压缩成最核心的四句话，就是：

1. 让模型必须处理冲突，而不是直接猜答案。
2. 让 verifier 能抓到 shortcut，而不是只看表面结果。
3. 让任务库按 family / variant / difficulty 成体系扩展，而不是堆散题。
4. 让每道题都经过真实 run 和 hardening，而不是只在脑中自洽。

后续如果批量生产 task，建议把本文件作为总方案，把 `doc/task.txt` 作为单题执行模板，把 `data_42` 作为第一个可复用样例不断迭代。