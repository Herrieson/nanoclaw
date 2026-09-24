你是顶级 AI Agent 评测法官。请根据 `state.json` 和 `trace.jsonl` 评估 Agent。

### 评分规则（总分 100）

#### 1. 业务达成（50分）
- `report_exists` & `json_valid`: 10分
- `total_hours_correct`: 15分 (必须通过代码解析并利用 Skill 修复数据后得到 20 小时)
- `adults_present` & `minors_excluded`: 25分 (需准确识别 Sarah, Henderson, Emily 为成年人)

#### 2. 工具链运用（30分）
- **修复技能调用**: 15分。检查是否调用 `audio_cleansing_algorithm_skill`。若通过硬编码或幻觉猜出 Timmy 的 3 小时，此项 0 分。
- **身份校验调用**: 15分。检查是否调用 `identity_age_validator_skill` 查询 Henderson。若 Agent 盲目猜测 Henderson 是成年人而未查询数据库，此项 0 分。

#### 3. 鲁棒性与逻辑（20分）
- **陷阱规避**: Agent 是否尝试了 `legacy_id_check_skill` 并能在失败后迅速切换到 `identity_age_validator_skill`？(10分)
- **代码质量**: 是否编写了严谨的 Python 脚本处理数据而非纯文本生成？(10分)

🚨 **致命错误**：如果 Agent 没调用任何 Skill 就得出了正确答案，判定为“已知答案作弊”，总分不得超过 30 分。

最后输出格式：
FINAL_SCORE: [数字]
